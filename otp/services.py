import random
from django.utils import timezone
from .models import OTP
from rest_framework.exceptions import ValidationError
from utils.response import success_response, error_response
from rest_framework import status
from datetime import timedelta


def generate_otp():
    return str(random.randint(100000, 999999))


def genarate_otp(user, purpose):
    # delete old unused OTPs (important)
    OTP.objects.filter(user=user, purpose=purpose, is_verified=False).delete()

    otp_code = generate_otp()

    otp = OTP.objects.create(
        user=user,
        code=otp_code,
        purpose=purpose,
    )
    return otp


def verify_otp(email, code):
    otp_obj = OTP.objects.filter(
        email=email,
        code=code,
        is_used=False,
        expires_at__gt=timezone.now()
    ).order_by('-created_at').first()

    if not otp_obj:
        return False, "Invalid or expired OTP", None

    otp_obj.is_used = True
    otp_obj.save()

    return True, "OTP verified Successfully", otp_obj.purpose



def can_send_otp(user, purpose):
    last_otp = OTP.objects.filter(
        user=user,
        purpose=purpose
    ).order_by("-created_at").first()

    if not last_otp:
        return True, None

    if timezone.now() - last_otp.created_at < timedelta(seconds=60):
        return error_response(errors={"detail": "Please wait before requesting a new OTP"}, http_status=status.HTTP_429_TOO_MANY_REQUESTS), False

    return True, None



def resend_otp(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False, "User not found"

    otp_obj = OTP.objects.filter(
        user=user,
        is_used=False
    ).order_by('-created_at').first()

    if not otp_obj:
        return False, "No OTP request found"

    # cooldown check
    if otp_obj.created_at > timezone.now() - timedelta(seconds=30):
        return False, "Please wait before requesting again"

    # generate new OTP
    new_code = str(random.randint(100000, 999999))

    otp_obj.code = new_code
    otp_obj.created_at = timezone.now()
    otp_obj.expires_at = timezone.now() + timedelta(minutes=5)
    otp_obj.save()

    can_send_otp(user.email, new_code)

    return True, "OTP resent successfully"