from datetime import datetime, timedelta, timezone


def get_iso_datetime_offset(hours: int = 0) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat() + "Z"


def parse_iso(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str.replace("Z", ""))
