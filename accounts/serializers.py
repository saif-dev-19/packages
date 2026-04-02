from rest_framework import serializers
from .models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")
        if value == self.initial_data.get("email"):
            raise serializers.ValidationError("Password cannot be the same as email")
        
        return value


#============================
#Change password serializer
#============================
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(min_length=6, required=True)

#============================
#Reset password serializer
#============================
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

#============================
# Reset password confirm serializer
# ============================
class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)    

#============================
##OTP verification serializer
#============================
from rest_framework import serializers
from otp.choices import OtpPurpose, OtpChannel

class OtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=OtpPurpose.choices)   #It will be given from frontend hardcoded to know the purpose of OTP 
    channel = serializers.ChoiceField(choices=OtpChannel.choices)  #It will be given from frontend hardcoded to know the channel of OTP (email/phone)

class OtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=OtpPurpose.choices) #It will be given from frontend hardcoded to know the purpose of OTP 
    otp = serializers.CharField(max_length=6)




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["email"] = user.email or ""
        token["first_name"] = getattr(user, "first_name", "") or ""
        token["last_name"] = getattr(user, "last_name", "") or ""

        return token