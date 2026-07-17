"""Pydantic Schema Engine — Example implementation.

IOP: This is an EXAMPLE. Users can implement their own with any library.
"""

from __future__ import annotations

from typing import Any


class PydanticValidator:
    """Pydantic-based validator. Requires: pip install pydantic"""

    def validate(self, data: Any, schema: type) -> Any:
        if hasattr(schema, "model_validate"):
            return schema.model_validate(data)
        return data

    def serialize(self, obj: Any) -> dict[str, Any]:
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if isinstance(obj, dict):
            return obj
        return {"value": obj}

    def deserialize(self, data: dict[str, Any], schema: type) -> Any:
        if hasattr(schema, "model_validate"):
            return schema.model_validate(data)
        return data
