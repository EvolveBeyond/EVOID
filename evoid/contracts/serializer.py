"""Serializer Engine — Interface for serialization.

IOP: Contract only. Behavior lives in engines/.
"""

from __future__ import annotations

from typing import Any, Protocol


class SerializerEngine(Protocol):
    """Protocol for serializer engines."""

    def encode(self, data: Any) -> bytes: ...
    def decode(self, data: bytes, schema: type | None = None) -> Any: ...
