"""JSON Serializer — Pure functions, IOP compliant.

IOP: Data carries intent. Serializer adapts to data.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID


def _default(obj: Any) -> Any:
    """Handle types json.dumps can't serialize."""
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


def encode(data: Any) -> bytes:
    """Encode data to JSON bytes."""
    return json.dumps(data, default=_default, ensure_ascii=False).encode("utf-8")


def decode(data: bytes, schema: type | None = None) -> Any:
    """Decode JSON bytes to data."""
    return json.loads(data.decode("utf-8"))


class JsonSerializer:
    """Adapter for SerializerEngine protocol."""

    def encode(self, data: Any) -> bytes:
        return encode(data)

    def decode(self, data: bytes, schema: type | None = None) -> Any:
        return decode(data, schema)
