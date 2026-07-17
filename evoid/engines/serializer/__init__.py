"""Serializer engines — Pluggable serialization layer.

IOP: EVOID provides the interface. Users bring their own library.
Just implement the Serializer protocol and register it.
"""

from __future__ import annotations

from ...contracts.serializer import Serializer

# Global registry
_serializer: Serializer | None = None


def get_serializer() -> Serializer:
    """Get the active serializer. Falls back to stdlib json."""
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

    from .json_engine import JsonSerializer
    return JsonSerializer()


def set_serializer(serializer: Serializer) -> None:
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
