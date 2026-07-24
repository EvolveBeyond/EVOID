"""Msgpack Serializer — Binary serialization, 2-5x faster than JSON.

IOP: Optional engine for high-performance API communication.
Install: pip install msgpack or evoid[msgpack]

Benefits over JSON:
- 2-5x smaller payload size
- 2-5x faster encode/decode
- Binary format (no string parsing overhead)
- Native support for bytes, datetime, sets
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

import msgpack


def _default(obj: Any) -> Any:
    """Handle types msgpack can't serialize natively."""
    if isinstance(obj, (datetime, date, time)):
        return {"__type__": "datetime", "value": obj.isoformat()}
    if isinstance(obj, UUID):
        return {"__type__": "uuid", "value": str(obj)}
    if isinstance(obj, Decimal):
        return {"__type__": "decimal", "value": str(obj)}
    if isinstance(obj, bytes):
        return {"__type__": "bytes", "value": obj.decode("utf-8", errors="replace")}
    if isinstance(obj, set):
        return {"__type__": "set", "value": list(obj)}
    if isinstance(obj, frozenset):
        return {"__type__": "frozenset", "value": list(obj)}
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


def _object_hook(obj: dict) -> Any:
    """Restore types from msgpack encoding."""
    if "__type__" in obj:
        t = obj["__type__"]
        v = obj["value"]
        if t == "datetime":
            return datetime.fromisoformat(v)
        if t == "date":
            return date.fromisoformat(v)
        if t == "time":
            return time.fromisoformat(v)
        if t == "uuid":
            return UUID(v)
        if t == "decimal":
            return Decimal(v)
        if t == "bytes":
            return v.encode("utf-8")
        if t == "set":
            return set(v)
        if t == "frozenset":
            return frozenset(v)
    return obj


class MsgpackSerializer:
    """Msgpack-based serializer.

    Requires: pip install msgpack

    Benefits:
    - 2-5x smaller payloads than JSON
    - 2-5x faster encode/decode
    - Binary format (no string parsing)
    - Native bytes support (no base64 overhead)
    """

    def __init__(
        self,
        use_bin_type: bool = True,
        max_buffer_size: int = 100 * 1024 * 1024,  # 100MB
    ):
        self._packer = msgpack.Packer(
            default=_default,
            use_bin_type=use_bin_type,
        )
        self._max_buffer_size = max_buffer_size

    def encode(self, data: Any) -> bytes:
        """Encode data to msgpack bytes."""
        return self._packer.pack(data)

    def decode(self, data: bytes, schema: type | None = None) -> Any:
        """Decode msgpack bytes to data.

        Args:
            data: Msgpack bytes
            schema: Optional schema for validation (ignored in msgpack,
                    but kept for API compatibility with JSON serializer)
        """
        return msgpack.unpackb(
            data,
            object_hook=_object_hook,
            raw=False,
        )


def register_handlers() -> None:
    """Register Msgpack serializer as the default serializer engine."""
    from ..handler import set_handler
    instance = MsgpackSerializer()
    set_handler("serializer", "serializer.encode", {"instance": instance})
    set_handler("serializer", "serializer.decode", {"instance": instance})
