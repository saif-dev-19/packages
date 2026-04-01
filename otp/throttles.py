from django.core.cache import cache
from rest_framework.throttling import BaseThrottle
import time


class RedisOtpThrottle(BaseThrottle):
    rate = 3  # requests
    duration = 60  # seconds

    def allow_request(self, request, view):
        email = request.data.get("email")
        if not email:
            return True

        key = f"otp_throttle:{email}"

        history = cache.get(key, [])

        now = time.time()

        # remove expired timestamps
        history = [t for t in history if now - t < self.duration]

        if len(history) >= self.rate:
            return False

        history.append(now)
        cache.set(key, history, timeout=self.duration)

        return True