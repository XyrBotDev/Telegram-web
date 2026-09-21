from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


def utc_isoformat() -> str:
    """Return the current UTC time as an ISO string."""
    return utc_now().isoformat()


def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """Convert a value to integer safely."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_str(
    value: Any,
    default: str = "",
) -> str:
    """Convert a value to string safely."""
    if value is None:
        return default

    return str(value)


def chunk_list(
    items: list[Any],
    size: int,
) -> list[list[Any]]:
    """Split a list into fixed-size chunks."""
    if size <= 0:
        raise ValueError(
            "Chunk size must be greater than zero."
        )

    return [
        items[index:index + size]
        for index in range(0, len(items), size)
    ]
