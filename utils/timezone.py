from datetime import datetime
from zoneinfo import ZoneInfo
from django.utils import timezone
from datetime import timezone as dt_timezone

def to_utc(dt: datetime, user_tz: str = "UTC"):
    """
    Convert user local datetime → UTC safely
    """
    if dt is None:
        return None

    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    try:
        tz = ZoneInfo(user_tz)
    except Exception:
        tz = ZoneInfo("UTC")

    dt = dt.replace(tzinfo=tz)

    return dt.astimezone(dt_timezone.utc)