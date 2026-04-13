from datetime import UTC, datetime


def ensure_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    return require_utc_datetime(value)


def require_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)

    return value.astimezone(UTC)
