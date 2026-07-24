"""Msgspec Serializer — Pure functions, IOP compliant.

IOP: Fastest JSON serializer. Requires: pip install msgspec
"""

from __future__ import annotations

from typing import Any


def encode(data: Any) -> bytes:
    """Encode data using msgspec."""
    import msgspec
    return msgspec.json.encode(data)


def decode(data: bytes, schema: type | None = None) -> Any:
    """Decode data using msgspec with optional type validation."""
    import msgspec
    if schema:
        return msgspec.json.decode(data, type=schema)
    return msgspec.json.decode(data)


class MsgspecSerializer:
    """Adapter for SerializerEngine protocol."""

    def encode(self, data: Any) -> bytes:
        return encode(data)

    def decode(self, data: bytes, schema: type | None = None) -> Any:
        return decode(data, schema)
