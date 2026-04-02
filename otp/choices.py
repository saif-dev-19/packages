from django.db import models


class OtpPurpose(models.TextChoices):
    REGISTRATION = "registration", "Registration"
    PASSWORD_RESET = "password_reset", "Password Reset"
    EMAIL_VERIFICATION = "email_verification", "Email Verification"


class OtpChannel(models.TextChoices):
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"