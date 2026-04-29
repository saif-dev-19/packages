from .models import OtpPurpose
from utils.email import send_purpose_email
from django.template.loader import render_to_string


def send_otp_email(user, otp):
    context = {"user_email": user.email, "otp_code": otp.code}

    if otp.purpose == OtpPurpose.REGISTRATION:
        subject = "Verify your account"
        html_content = render_to_string("register.html", context)
        text_content = f"Your registration OTP is: {otp.code}"

    elif otp.purpose == OtpPurpose.PASSWORD_RESET:
        subject = "Reset your password"
        html_content = render_to_string("reset_password.html", context)
        text_content = f"Your reset OTP is: {otp.code}"

    else:  # LOGIN
        subject = "Login OTP"
        html_content = render_to_string("login_otp.html", context)
        text_content = f"Your login OTP is: {otp.code}"

    send_purpose_email(user.email, subject, text_content, html_content)