"""Msgspec Schema Engine — Example implementation.

IOP: This is an EXAMPLE. Users can implement their own with any library.
"""

from __future__ import annotations

from typing import Any


class MsgspecValidator:
    """Msgspec-based validator. Requires: pip install msgspec"""

    def validate(self, data: Any, schema: type) -> Any:
        import msgspec
        if isinstance(data, dict):
            return msgspec.convert(data, schema)
        return data

    def serialize(self, obj: Any) -> dict[str, Any]:
        import msgspec
        if hasattr(obj, "__struct_fields__"):
            return msgspec.to_builtins(obj)
        if isinstance(obj, dict):
            return obj
        return {"value": obj}

    def deserialize(self, data: dict[str, Any], schema: type) -> Any:
        import msgspec
        return msgspec.convert(data, schema)
