"""Storage Engine — Interface for data persistence.

IOP: Contract only. Behavior lives in engines/.
"""

from __future__ import annotations

from typing import Any, Protocol


class StorageEngine(Protocol):
    """Protocol for storage engines."""

    async def read(self, key: str) -> Any | None: ...
    async def write(self, key: str, value: Any) -> bool: ...
    async def delete(self, key: str) -> bool: ...
    async def health(self) -> bool: ...
