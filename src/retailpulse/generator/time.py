"""Deterministic timestamp utilities."""

from datetime import datetime, timedelta


def timestamp_from_index(
    start_time: datetime,
    index: int,
    interval_seconds: int = 60,
) -> datetime:
    """Generate a timestamp from a stable entity index."""

    if start_time.tzinfo is None:
        raise ValueError("start_time must be timezone-aware.")

    if index < 0:
        raise ValueError("index must not be negative.")

    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be strictly positive.")

    return start_time + timedelta(seconds=index * interval_seconds)


def to_epoch_millis(value: datetime) -> int:
    """Convert a timezone-aware timestamp to Unix milliseconds."""

    if value.tzinfo is None:
        raise ValueError("value must be timezone-aware.")

    return int(value.timestamp() * 1000)
