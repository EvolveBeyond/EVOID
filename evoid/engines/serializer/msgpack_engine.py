"""Msgpack Serializer — Pure functions, IOP compliant.

IOP: Serializer is data + functions, not stateful objects.
The Intent lives in the data being serialized.

Benefits over JSON:
- 2-5x smaller payload size
- 2-5x faster encode/decode
- Binary format (no string parsing overhead)
- Native support for bytes, datetime, sets

Install: pip install msgpack or evoid[msgpack]
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID


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


def encode(data: Any) -> bytes:
    """Encode data to msgpack bytes.

    IOP: Pure function. Intent is in the data, not the serializer.
    """
    import msgpack
    return msgpack.packb(data, default=_default, use_bin_type=True)


def decode(data: bytes, schema: type | None = None) -> Any:
    """Decode msgpack bytes to data.

    IOP: Pure function. Schema validation is Intent-driven.
    """
    import msgpack
    return msgpack.unpackb(data, object_hook=_object_hook, raw=False)


class MsgpackSerializer:
    """Msgpack adapter for SerializerEngine protocol.

    IOP: Adapter pattern — adapts pure functions to protocol interface.
    The Intent lives in the data being serialized, not here.
    """

    def encode(self, data: Any) -> bytes:
        return encode(data)

    def decode(self, data: bytes, schema: type | None = None) -> Any:
        return decode(data, schema)
