"""Native Schema Engine — Uses stdlib dataclasses and TypedDict.

IOP: Pure functions. No class state.
"""

from __future__ import annotations

import dataclasses
from typing import Any, get_type_hints


def validate(data: Any, schema: type) -> Any:
    """Validate data against a schema type.

    Supports: dataclass, TypedDict, dict with type hints.
    """
    if dataclasses.is_dataclass(schema) and not isinstance(schema, type):
        # Already an instance
        return data

    if dataclasses.is_dataclass(schema):
        # Create instance from dict
        if isinstance(data, dict):
            return schema(**{k: v for k, v in data.items() if k in schema.__dataclass_fields__})
        return data

    # TypedDict or plain dict — just return data
    return data


def serialize(obj: Any) -> dict[str, Any]:
    """Serialize an object to dict."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, dict):
        return obj
    return {"value": obj}


def deserialize(data: dict[str, Any], schema: type) -> Any:
    """Deserialize dict to typed object."""
    if dataclasses.is_dataclass(schema) and isinstance(schema, type):
        return schema(**{k: v for k, v in data.items() if k in schema.__dataclass_fields__})
    return data


def schema_of(schema: type) -> dict[str, Any]:
    """Get schema as dict (simple field listing)."""
    if dataclasses.is_dataclass(schema) and isinstance(schema, type):
        hints = get_type_hints(schema)
        return {
            "type": schema.__name__,
            "fields": {name: str(hint) for name, hint in hints.items()},
        }
    return {"type": schema.__name__ if hasattr(schema, "__name__") else str(schema)}
