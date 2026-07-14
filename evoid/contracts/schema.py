"""Schema Engine — Interface for schema validation.

IOP: This is a contract, not behavior.
Implementations live in engines/, not here.
"""

from __future__ import annotations

from typing import Any, Protocol


class SchemaEngine(Protocol):
    """Protocol for schema validation engines."""

    def validate(self, data: Any, schema: type) -> Any: ...
    def serialize(self, obj: Any) -> dict[str, Any]: ...
    def deserialize(self, data: dict[str, Any], schema: type) -> Any: ...
