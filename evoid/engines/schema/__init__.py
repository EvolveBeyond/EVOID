"""Schema engines — Pluggable validation layer.

IOP: EVOID provides the interface. Users bring their own library.
Just implement the SchemaEngine protocol and register it.
"""

from __future__ import annotations

from typing import Any

from ...contracts.schema import SchemaEngine
from .native import deserialize as _deserialize
from .native import serialize as _serialize
from .native import validate as _validate

_validator: SchemaEngine | None = None


def get_validator() -> SchemaEngine:
    """Get the active validator. Falls back to stdlib dataclasses."""
    global _validator
    if _validator is not None:
        return _validator

    try:
        from .msgspec_engine import MsgspecValidator
        return MsgspecValidator()
    except ImportError:
        pass

    try:
        from .pydantic_engine import PydanticValidator
        return PydanticValidator()
    except ImportError:
        pass

    return _NativeValidator()


def set_validator(validator: SchemaEngine) -> None:
    """Register a custom validator."""
    global _validator
    _validator = validator


def reset_validator() -> None:
    """Reset to auto-detection."""
    global _validator
    _validator = None


class _NativeValidator:
    """Wrapper for native functions to match SchemaEngine protocol."""

    def validate(self, data: Any, schema: type) -> Any:
        return _validate(data, schema)

    def serialize(self, obj: Any) -> dict[str, Any]:
        return _serialize(obj)

    def deserialize(self, data: dict[str, Any], schema: type) -> Any:
        return _deserialize(data, schema)
