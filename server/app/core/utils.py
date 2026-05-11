from datetime import timedelta, timezone
from typing import Optional


LOCAL_TIMEZONE = timezone(timedelta(hours=8))


def dt_to_local_str(dt) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
