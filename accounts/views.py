from datetime import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from otp.email_services import send_otp_email
from utils.response import error_response, success_response

from .serializers import ChangePasswordSerializer, RegisterSerializer, ResetPasswordConfirmSerializer, VerifyOtpSerializer,ResetPasswordSerializer
from .models import User

from otp.services import verify_otp
from otp.models import OtpPurpose
from rest_framework.throttling import UserRateThrottle
from django.db import transaction
from otp.throttles import RedisOtpThrottle
from otp.services import can_send_otp, genarate_otp
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated



class VerifyOtpThrottle(UserRateThrottle):
    rate = "10/min"


#============================
#Register and OTP verification view
#============================
class RegisterView(APIView):
    throttle_classes = [RedisOtpThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        with transaction.atomic():
            user, created = User.objects.get_or_create(email=email)

            if not created and user.is_active:
                return success_response(message="Email already registered", http_status=status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            if user.is_staff or user.is_superuser:
                user.is_active = True
            else:
                user.is_active = False
            user.save()

        can_send, error = can_send_otp(user, OtpPurpose.REGISTRATION)
        if not can_send:
            return error_response(errors={"error": error},message="Otp can not able to send.", http_status=status.HTTP_400_BAD_REQUEST)

        otp = genarate_otp(user, OtpPurpose.REGISTRATION)
        send_otp_email(user, otp)

        return success_response(message="OTP sent", http_status=status.HTTP_201_CREATED)

#============================
#Login View
#============================
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if not user:
            return error_response(errors={"error": "Invalid credentials"}, http_status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return error_response(errors={"error": "Account not verified"}, http_status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)

        return success_response(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            message="Login successful"
        )

#=============================
#Change password view
#=============================
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return error_response(errors={"error": "Old password is incorrect"}, http_status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return success_response(message="Password changed successfully")
    

#=============================
#Reset password view
#=============================
class ResetPasswordRequestView(APIView):
    throttle_classes = [RedisOtpThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Do not reveal if user exists
            return error_response(errors={"message": "If the email exists, an OTP has been sent"}, http_status=status.HTTP_200_OK)

        can_send, error = can_send_otp(user, OtpPurpose.PASSWORD_RESET)
        if not can_send:
            return error_response(errors={"error": error}, http_status=status.HTTP_400_BAD_REQUEST)

        otp = genarate_otp(user, OtpPurpose.PASSWORD_RESET)
        send_otp_email(user, otp)

        return error_response(errors={"message": "OTP sent if user exists"}, http_status=status.HTTP_200_OK)


#=============================
#Reset password confirm view
#=============================
class ResetPasswordConfirmView(APIView):
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp_code = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response(errors={"error": "Invalid email"}, http_status=status.HTTP_400_BAD_REQUEST)

        success, message = verify_otp(user, otp_code, OtpPurpose.PASSWORD_RESET)

        if not success:
            return error_response(errors={"error": message}, http_status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return success_response(message="Password reset successfully")


#=============================
#logout view
#=============================
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return success_response(message="Logged out successfully")
        except Exception:
            return error_response(errors={"error": "Invalid token"}, http_status=status.HTTP_400_BAD_REQUEST)


#============================
#OTP Verification View
#============================  
from otp.models import OTP, OtpPurpose


class VerifyOtpView(APIView):
    throttle_classes = [VerifyOtpThrottle]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["otp"]

        success, message, purpose = verify_otp(email, code)

        if not success:
            return error_response({"error": message}, 400)

        user = User.objects.filter(email=email).first()
        if not user:
            return error_response({"error": "User not found"}, 404)

        # handle based on purpose internally
        if purpose == OtpPurpose.REGISTRATION:
            user.is_active = True
            user.save()

        return success_response(message="OTP verified successfully")


class ResendOtpView(APIView):
    throttle_classes = [RedisOtpThrottle]

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        otp_purpose = OTP.objects.filter(user=user, is_verified=False).order_by("-created_at").first()
        if not email:
            return error_response({"error": "Email is required"}, http_status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response({"error": "User not found"}, http_status=404)
        
        print("OTP Purpose==============+++++++>", otp_purpose)

        can_send, error = can_send_otp(user, otp_purpose.purpose )
        if not can_send:
            return error_response({"error": error}, http_status=400)

        otp = genarate_otp(user, otp_purpose.purpose if otp_purpose else None)
        send_otp_email(user, otp)

        return success_response(message="OTP resent successfully")