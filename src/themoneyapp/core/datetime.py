"""Helpers to manage datetime objects."""

from __future__ import annotations

import datetime as dt


def aware_utcnow() -> dt.datetime:
    """Construct a timezone (UTC) aware datetime."""
    return dt.datetime.now(dt.timezone.utc)


def aware_utcfromtimestamp(timestamp: float) -> dt.datetime:
    """Construct a timezone (UTC) aware datetime from a POSIX timestamp."""
    return dt.datetime.fromtimestamp(timestamp, dt.timezone.utc)


def naive_utcnow() -> dt.datetime:
    """Construct a non-timezone aware datetime in UTC."""
    return aware_utcnow().replace(tzinfo=None)


def naive_utcfromtimestamp(timestamp: float) -> dt.datetime:
    """Construct a non-timezone aware datetime in UTC from a POSIX timestamp."""
    return aware_utcfromtimestamp(timestamp).replace(tzinfo=None)


def isoformat(o: dt.date | dt.time) -> str:
    """Return the date formatted according to ISO."""
    return o.isoformat()
