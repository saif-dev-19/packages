from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions
import logging

from .models import Task, TaskStatus
from .tasks import send_task_completed_event
from utils.email import send_purpose_email

logger = logging.getLogger(__name__)


def send_task_completed_email(*, task_id: int, title: str, email: str) -> None:
    if not email:
        logger.warning("Task completed email skipped because email is empty. task_id=%s", task_id)
        return

    subject = "Task completed"
    text_content = f"Your task '{title}' has been marked as completed."

    send_purpose_email(
        to_email=email,
        subject=subject,
        text_content=text_content,
    )


def complete_task(*, task: Task) -> Task:
    if task.status == TaskStatus.COMPLETED:
        raise exceptions.ValidationError("Task is already completed.")

    with transaction.atomic():
        task.status = TaskStatus.COMPLETED
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at", "updated_at"])

        task_id = task.id
        title = task.title
        email = task.created_by_email

        transaction.on_commit(
            lambda: enqueue_task_completed_email(
                task_id=task_id,
                user_id=task.created_by_user_id,
                title=title,
                email=email,
            )
        )

    return task


def enqueue_task_completed_email(*, task_id: int, user_id: int, title: str, email: str) -> None:
    try:
        send_task_completed_event.delay(
            task_id=task_id,
            user_id=user_id,
            title=title,
            email=email,
        )
    except Exception:
        logger.exception(
            "Could not enqueue task completed email. Sending directly. task_id=%s user_id=%s",
            task_id,
            user_id,
        )
        send_task_completed_email(
            task_id=task_id,
            title=title,
            email=email,
        )
