import jwt
from django.conf import settings
from rest_framework import authentication, exceptions


class ServiceUser:
    def __init__(self, user_id, email=None):
        self.id = user_id
        self.email = email or ""

    @property
    def is_authenticated(self):
        return True


class JWTServiceAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.")

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SHARED_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired.")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token.")

        if payload.get("token_type") != "access":
            raise exceptions.AuthenticationFailed("Only access tokens are allowed.")

        user_id = payload.get("user_id")
        email = payload.get("email", "")

        if user_id is None:
            raise exceptions.AuthenticationFailed("Token missing user_id.")

        return ServiceUser(user_id=user_id, email=email), payload