from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions

from .models import Task, TaskStatus
from .tasks import send_task_completed_event


def complete_task(*, task: Task) -> Task:
    if task.status == TaskStatus.COMPLETED:
        raise exceptions.ValidationError("Task is already completed.")

    with transaction.atomic():
        task.status = TaskStatus.COMPLETED
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at", "updated_at"])

        transaction.on_commit(
            lambda: send_task_completed_event.delay(
                task_id=task.id,
                user_id=task.created_by_user_id,
                title=task.title,
                email=task.created_by_email,
            )
        )
        print(f"Task {task.id} marked as completed. Event scheduled to be sent.{task.created_by_email}")

    return task