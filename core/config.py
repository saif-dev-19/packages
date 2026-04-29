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
    JWT_SHARED_SECRET: str = config("JWT_SHARED_SECRET")
    JWT_ALGORITHM: str = config("JWT_ALGORITHM", default="HS256")

    # Redis Cache
    REDIS_URL: str = config("REDIS_URL", default="redis://redis:6379/1")
    REDIS_HOST: str = config("REDIS_HOST", default="127.0.0.1")
    REDIS_PORT: int = config("REDIS_PORT", default=6379, cast=int)
    REDIS_DB: int = config("REDIS_DB", default=1, cast=int)


    CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://redis:6379/0")
    CELERY_ACCEPT_CONTENT: list = config("CELERY_ACCEPT_CONTENT", default=["json"], cast=Csv())
    CELERY_TASK_SERIALIZER: str = config("CELERY_TASK_SERIALIZER", default="json")
    CELERY_RESULT_SERIALIZER: str = config("CELERY_RESULT_SERIALIZER", default="json")
    CELERY_TIMEZONE: str = config("CELERY_TIMEZONE", default="UTC")


    # Optional: Add more configs here
    DEBUG: bool = config("DEBUG", default=True, cast=bool)
    SECRET_KEY: str = config("SECRET_KEY", default="change-me-in-prod")

    OTP_EXPIRY_MINUTES: int = config("OTP_EXPIRY_MINUTES", default=5, cast=int)
    OTP_LENGTH: int = config("OTP_LENGTH", default=6, cast=int)

#=============================
# Database configuration
#=============================
    DB_ENGINE = "django.db.backends.postgresql"
    DB_NAME = config("DB_NAME")
    DB_USER = config("DB_USER")
    DB_PASSWORD = config("DB_PASSWORD")
    DB_HOST = config("DB_HOST", default="127.0.0.1")
    DB_PORT = config("DB_PORT", default="5432")