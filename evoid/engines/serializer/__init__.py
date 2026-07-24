"""Serializer engines — Pluggable serialization layer.

IOP: EVOID provides the interface. Users bring their own library.
Just implement the Serializer protocol and register it.
"""

from __future__ import annotations

from ...contracts.serializer import SerializerEngine

# Global registry
_serializer: SerializerEngine | None = None


def get_serializer() -> SerializerEngine:
    """Get the active serializer. Falls back to stdlib json.

    Auto-detection order:
    1. Custom serializer (set via set_serializer)
    2. msgspec (fastest JSON)
    3. orjson (fast JSON)
    4. pydantic (schema validation)
    5. msgpack (binary, smallest payload)
    6. stdlib json (always available)
    """
    global _serializer
    if _serializer is not None:
        return _serializer

    # Auto-detect best available
    try:
        from .msgspec_engine import MsgspecSerializer
        return MsgspecSerializer()
    except ImportError:
        pass

    try:
        from .orjson_engine import OrjsonSerializer
        return OrjsonSerializer()
    except ImportError:
        pass

    try:
        from .pydantic_engine import PydanticSerializer
        return PydanticSerializer()
    except ImportError:
        pass

    # Check if user configured msgpack as preferred
    try:
        from ...config.loader import load as load_config
        config = load_config()
        if config.engines.serializer == "msgpack":
            from .msgpack_engine import MsgpackSerializer
            return MsgpackSerializer()
    except Exception:
        pass

    from .json_engine import JsonSerializer
    return JsonSerializer()


def set_serializer(serializer: SerializerEngine) -> None:
    """Register a custom serializer.

    Usage:
        from evoid.engines.serializer import set_serializer
        from mylib import MySerializer

        set_serializer(MySerializer())
    """
    global _serializer
    _serializer = serializer


def reset_serializer() -> None:
    """Reset to auto-detection."""
    global _serializer
    _serializer = None
