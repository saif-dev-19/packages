from datetime import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from otp.email_services import send_otp_email
from utils.response import error_response, success_response

from .serializers import ChangePasswordSerializer, RegisterSerializer, ResetPasswordConfirmSerializer,ResetPasswordSerializer
from .models import User
from otp.choices import OtpPurpose, OtpChannel
from otp.services import OTPService
from rest_framework.throttling import UserRateThrottle
from django.db import transaction
from otp.throttles import RedisOtpThrottle
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
                return success_response(
                    message="Email already registered",
                    http_status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(password)
            # staff/superuser are active immediately
            user.is_active = user.is_staff or user.is_superuser
            user.save()

        # Send OTP via email using OTPService
        success, msg = OTPService.send_otp(
            email=email,
            purpose=OtpPurpose.REGISTRATION,
            channel=OtpChannel.EMAIL
        )

        if not success:
            return error_response(
                errors={"error": msg},
                message="OTP could not be sent",
                http_status=status.HTTP_400_BAD_REQUEST
            )

        return success_response(
            message="OTP sent successfully",
            http_status=status.HTTP_201_CREATED
        )

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
# accounts/views.py

class ResetPasswordRequestView(APIView):
    throttle_classes = [RedisOtpThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Do not reveal user existence
        user_exists = User.objects.filter(email=email).exists()

        if user_exists:
            success, msg = OTPService.send_otp(
                email=email,
                purpose=OtpPurpose.PASSWORD_RESET,
                channel=OtpChannel.EMAIL
            )

            if not success:
                return error_response(
                    errors={"error": msg},
                    http_status=status.HTTP_400_BAD_REQUEST
                )

        return success_response(
            message="If the email exists, an OTP has been sent",
            http_status=status.HTTP_200_OK
        )


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
            return error_response(
                errors={"error": "Invalid email"},
                http_status=status.HTTP_400_BAD_REQUEST
            )

        success, message = OTPService.verify_otp(
            email=email,
            purpose=OtpPurpose.PASSWORD_RESET,
            submitted_otp=otp_code
        )

        if not success:
            return error_response(
                errors={"error": message},
                http_status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return success_response(
            message="Password reset successfully",
            http_status=status.HTTP_200_OK
        )


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
# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from otp.services import OTPService
from accounts.serializers import OtpSerializer, OtpVerifySerializer

class OTPView(APIView):
    """
    Get / Resend OTP
    """
    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        purpose = serializer.validated_data["purpose"]
        channel = serializer.validated_data["channel"]

        if purpose == OtpPurpose.REGISTRATION:
            if User.objects.filter(email=email, is_active=True).exists():
                return Response({"error": "Email already verified"}, status=status.HTTP_400_BAD_REQUEST)

            if not User.objects.filter(email=email).exists():
                return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
            
        success, msg = OTPService.send_otp(email, purpose, channel)

        if not success:
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": msg}, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    """
    Verify OTP
    """
    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        purpose = serializer.validated_data["purpose"]
        otp = serializer.validated_data["otp"]

        success, msg = OTPService.verify_otp(email, purpose, otp)

        if success:
            if purpose == OtpPurpose.REGISTRATION:
                try:
                    user = User.objects.get(email=email)
                    user.is_active = True
                    user.save()
                except User.DoesNotExist:
                    pass

        if not success:
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": msg}, status=status.HTTP_200_OK)