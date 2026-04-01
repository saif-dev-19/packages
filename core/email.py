from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_purpose_email(to_email, subject, text_content, html_content=None):
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )

    if html_content:
        email.attach_alternative(html_content, "text/html")

    email.send()