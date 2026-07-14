"""Cache Engine — Interface for caching.

IOP: Contract only. Behavior lives in engines/.
"""

from __future__ import annotations

from typing import Any, Protocol


class CacheEngine(Protocol):
    """Protocol for cache engines."""

    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: float | None = None) -> bool: ...
    async def delete(self, key: str) -> bool: ...
    async def health(self) -> bool: ...
