from django.utils import timezone

from celery import shared_task
import logging
from .models import Task

from utils.email import send_purpose_email

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_task_completed_event(self, task_id, user_id, title, email=""):
    logger.info(
        "Task completed event triggered. task_id=%s user_id=%s title=%s email=%s",
        task_id,
        user_id,
        title,
        email,
    )

    if not email:
        logger.warning(
            "Task completed email skipped because recipient email is empty. task_id=%s user_id=%s",
            task_id,
            user_id,
        )
        return {
            "task_id": task_id,
            "user_id": user_id,
            "title": title,
            "email": email,
            "email_sent": False,
        }
    

    subject = "Task completed"
    text_content = f"Your task '{title}' has been marked as completed."

    send_purpose_email(
        to_email=email,
        subject=subject,
        text_content=text_content,
    )

    # Later this will:
    # 1. notify notification_service
    # 2. publish to Redis / HTTP / queue
    # 3. maybe send websocket event indirectly

    return {
        "task_id": task_id,
        "user_id": user_id,
        "title": title,
        "email": email,
        "email_sent": True,
    }   


from .choices import TaskStatus
from django.core.cache import cache

@shared_task
def mark_overdue_tasks():
    overdue_tasks = Task.objects.filter(
        status__in=[
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS
        ],
        due_date__lt=timezone.now()
    )

    user_ids = overdue_tasks.values_list(
        "created_by_user_id",
        flat=True
    ).distinct()
    print(f"Marking {overdue_tasks.count()} tasks as overdue for users: {list(user_ids)}")
    updated_count = overdue_tasks.update(
        status=TaskStatus.OVERDUE
    )

    for user_id in user_ids:
        cache.delete(f"task_list_user_{user_id}")

    return f"{updated_count} tasks marked overdue"