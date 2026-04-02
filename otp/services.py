# accounts/services/otp_service.py
import random
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

from core.redis_client import redis_client
from otp.choices import OtpPurpose, OtpChannel

class OTPService:

    OTP_TTL = getattr(settings, "OTP_EXPIRY_MINUTES", 5) * 60  # seconds
    COOLDOWN = 30  # seconds between OTP requests

    # Redis keys
    @staticmethod
    def _otp_key(email: str, purpose: str):
        return f"otp:{purpose}:{email}"

    @staticmethod
    def _cooldown_key(email: str, purpose: str):
        return f"otp_cooldown:{purpose}:{email}"

    # Generate random 6-digit OTP
    @staticmethod
    def _generate_otp():
        return str(random.randint(100000, 999999))

    # Get / resend OTP
    @classmethod
    def get_otp(cls, email: str, purpose: OtpPurpose):
        otp_key = cls._otp_key(email, purpose)
        cooldown_key = cls._cooldown_key(email, purpose)

        if redis_client.get(cooldown_key):
            return False, "Please wait before requesting OTP again"

        otp = cls._generate_otp()
        redis_client.setex(otp_key, cls.OTP_TTL, otp)
        redis_client.setex(cooldown_key, cls.COOLDOWN, "1")

        return True, otp

    # Verify OTP
    @classmethod
    def verify_otp(cls, email: str, purpose: OtpPurpose, submitted_otp: str):
        otp_key = cls._otp_key(email, purpose)
        stored_otp = redis_client.get(otp_key)

        if not stored_otp:
            return False, "OTP expired or not found"

        if stored_otp != submitted_otp:
            return False, "Invalid OTP"

        redis_client.delete(otp_key)
        return True, "OTP verified successfully"

    # Send OTP via email
    @classmethod
    def send_otp(cls, email: str, purpose: OtpPurpose, channel: OtpChannel):
        success, otp_or_msg = cls.get_otp(email, purpose)
        if not success:
            return False, otp_or_msg

        otp = otp_or_msg

        if channel == OtpChannel.EMAIL:
            # Use Django's send_mail
            subject = f"Your OTP for {purpose.title()}"
            message = f"Your OTP code is {otp}. It expires in {cls.OTP_TTL//60} minutes."
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
                recipient_list=[email],
            )
        elif channel == OtpChannel.PHONE:
            raise NotImplementedError("SMS not implemented")

        return True, "OTP sent successfully"