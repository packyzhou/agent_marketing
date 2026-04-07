from datetime import timezone
from typing import Optional


def dt_to_local_str(dt) -> Optional[str]:
    """Convert a naive UTC datetime (from DB) to local-timezone ISO string."""
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%Y-%m-%d %H:%M:%S")
