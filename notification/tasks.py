from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_overdue_email(email, task_title):
    send_mail(
        subject="Task Overdue Alert",
        message=f"Your task '{task_title}' is overdue.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )