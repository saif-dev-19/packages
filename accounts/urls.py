from django.urls import path
from .views import ChangePasswordView, ResetPasswordConfirmView, ResetPasswordRequestView, VerifyOtpView,ResendOtpView
from .views import RegisterView, LoginView, LogoutView



urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),
    path("reset-password/", ResetPasswordRequestView.as_view()),
    path("reset-password-confirm/", ResetPasswordConfirmView.as_view()),
    path('otp-verify/', VerifyOtpView.as_view(), name='otp-verify'),
    path('otp-resend/', ResendOtpView.as_view(), name='otp-resend'),
]
    