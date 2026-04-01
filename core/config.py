from decouple import config, Csv
from datetime import timedelta

class Config:
    EMAIL_BACKEND = config("EMAIL_BACKEND")
    EMAIL_HOST = config("EMAIL_HOST")
    EMAIL_PORT = config("EMAIL_PORT", cast=int)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

    # JWT Settings
    ACCESS_TOKEN_LIFETIME_MINUTES: int = config("ACCESS_TOKEN_LIFETIME_MINUTES", default=30, cast=int)
    REFRESH_TOKEN_LIFETIME_DAYS: int = config("REFRESH_TOKEN_LIFETIME_DAYS", default=1, cast=int)
    AUTH_HEADER_TYPES: tuple = ("Bearer",)
    BLACKLIST_AFTER_ROTATION: bool = config("BLACKLIST_AFTER_ROTATION", default=True, cast=bool)

    # Redis Cache
    REDIS_URL: str = config("REDIS_URL", default="redis://127.0.0.1:6379/1")

    # Optional: Add more configs here
    DEBUG: bool = config("DEBUG", default=True, cast=bool)
    SECRET_KEY: str = config("SECRET_KEY", default="change-me-in-prod")

    OTP_EXPIRY_MINUTES: int = config("OTP_EXPIRY_MINUTES", default=5, cast=int)
    OTP_LENGTH: int = config("OTP_LENGTH", default=6, cast=int)