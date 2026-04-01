from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
# Create your models here.


class OtpPurpose(models.TextChoices):
    REGISTRATION = "REGISTRATION", "Registration"
    PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION", "Email Verification"



class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=OtpPurpose.choices)

    is_verified = models.BooleanField(default=False)

    attempts = models.IntegerField(default=0)  # NEW
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def is_blocked(self):
        return self.attempts >= 5  # max attempts