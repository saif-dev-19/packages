from django.urls import path
from .views import ChangePasswordView, CustomTokenObtainPairView, ResetPasswordConfirmView, ResetPasswordRequestView,OTPView, OTPVerifyView
from .views import RegisterView, LoginView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view(),name="login"),
    path("logout/", LogoutView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),
    path("reset-password/", ResetPasswordRequestView.as_view()),
    path("reset-password-confirm/", ResetPasswordConfirmView.as_view()),
    path('get-otp/', OTPView.as_view(), name='get-otp'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    # path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
    