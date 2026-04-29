from celery import shared_task
import logging

from utils.email import send_purpose_email

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_task_completed_event(self, task_id, user_id, title, email=""):
    print(f"Scheduling task completed event for task_id={task_id} to be sent to {email}")
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
    print(f"Sending task completed email to {email} for task_id={task_id}")
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
