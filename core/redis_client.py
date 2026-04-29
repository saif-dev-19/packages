import redis
from django.conf import settings

redis_client = redis.Redis.from_url(
    settings.CACHES["default"]["LOCATION"],
    decode_responses=True  # return string instead of bytes
)
