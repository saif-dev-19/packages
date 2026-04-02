from django.urls import path
from .views import ChangePasswordView, ResetPasswordConfirmView, ResetPasswordRequestView,OTPView, OTPVerifyView
from .views import RegisterView, LoginView, LogoutView



urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),
    path("reset-password/", ResetPasswordRequestView.as_view()),
    path("reset-password-confirm/", ResetPasswordConfirmView.as_view()),
    path('get-otp/', OTPView.as_view(), name='get-otp'),
    path('otp-verify/', OTPVerifyView.as_view(), name='otp-verify'),
]
    