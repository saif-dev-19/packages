from django.utils import timezone

from celery import shared_task
import logging
from .models import Task
from .choices import TaskStatus
from django.core.cache import cache
from celery import shared_task
from django.utils import timezone

from .models import Task
from .choices import TaskStatus
from notification.models import Notification
from django.db import transaction
from notification.tasks import send_overdue_email

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()


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



@shared_task
def mark_overdue_tasks():
    overdue_tasks = Task.objects.filter(
        status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        due_date__lt=timezone.now()
    )

    if not overdue_tasks.exists():
        return "No tasks marked overdue"

    user_ids = list(overdue_tasks.values_list("created_by_user_id", flat=True).distinct())

    # 1. update status
    updated_count = overdue_tasks.update(status=TaskStatus.OVERDUE)

    # 2. create notifications
    notifications = []

    for task in overdue_tasks:
        notifications.append(
            Notification(
                user_id=task.created_by_user_id,
                title="Task Overdue",
                message=f"Your task '{task.title}' is now overdue."
            )
        )
    
    send_overdue_email.delay(
        email=task.created_by_email,
        task_title=task.title,
    )

    #For Notification
    Notification.objects.bulk_create(notifications)

    async_to_sync(channel_layer.group_send)(
        f"user_{task.created_by_user_id}",
            {
                "type": "send_notification",
                "data": {
                    "title": "Task Overdue",
                    "message": f"Task '{task.title}' is overdue"
                    }
            }
        )

    return f"{updated_count} tasks marked overdue + notifications created"




