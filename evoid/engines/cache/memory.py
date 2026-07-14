"""Memory Cache Engine — LRU cache with TTL.

IOP: Simple dict with expiry. No class behavior.
"""

from __future__ import annotations

import time
from typing import Any


# Cache entries: key -> (value, expiry_time)
_cache: dict[str, tuple[Any, float | None]] = {}
_max_size: int = 1000


def configure(max_size: int = 1000) -> None:
    """Configure cache settings."""
    global _max_size
    _max_size = max_size


async def get(key: str) -> Any | None:
    """Get value from cache."""
    entry = _cache.get(key)
    if entry is None:
        return None

    value, expiry = entry
    if expiry and time.time() > expiry:
        del _cache[key]
        return None

    return value


async def set(key: str, value: Any, ttl: float | None = None) -> bool:
    """Set value in cache with optional TTL."""
    # Evict if full
    if len(_cache) >= _max_size and key not in _cache:
        _evict_oldest()

    expiry = time.time() + ttl if ttl else None
    _cache[key] = (value, expiry)
    return True


async def delete(key: str) -> bool:
    """Delete from cache."""
    if key in _cache:
        del _cache[key]
        return True
    return False


async def clear() -> bool:
    """Clear all cache entries."""
    _cache.clear()
    return True


async def health() -> bool:
    """Cache is always healthy."""
    return True


def _evict_oldest() -> None:
    """Remove oldest entry."""
    if _cache:
        oldest_key = next(iter(_cache))
        del _cache[oldest_key]
