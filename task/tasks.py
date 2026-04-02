from celery import shared_task
import logging

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
    

    # Later this will:
    # 1. notify notification_service
    # 2. publish to Redis / HTTP / queue
    # 3. maybe send websocket event indirectly

    return {
        "task_id": task_id,
        "user_id": user_id,
        "title": title,
        "email": email,
    }