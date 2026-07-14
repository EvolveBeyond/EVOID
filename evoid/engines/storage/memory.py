"""Memory Storage Engine — In-memory storage.

IOP: Just a dict wrapper. No class behavior.
"""

from __future__ import annotations

from typing import Any


# Module-level state — simple dict
_store: dict[str, Any] = {}


async def read(key: str) -> Any | None:
    """Read from memory."""
    return _store.get(key)


async def write(key: str, value: Any) -> bool:
    """Write to memory."""
    _store[key] = value
    return True


async def delete(key: str) -> bool:
    """Delete from memory."""
    if key in _store:
        del _store[key]
        return True
    return False


async def health() -> bool:
    """Memory is always healthy."""
    return True


def clear() -> None:
    """Clear all stored data."""
    _store.clear()
