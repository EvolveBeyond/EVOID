"""JSON Serializer Engine — Uses stdlib json.

IOP: Pure functions. No class state.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any


def encode(data: Any) -> bytes:
    """Encode data to JSON bytes."""
    return json.dumps(data, default=_default_serializer).encode("utf-8")


def decode(data: bytes, schema: type | None = None) -> Any:
    """Decode JSON bytes to data."""
    return json.loads(data.decode("utf-8"))


def _default_serializer(obj: Any) -> Any:
    """Handle non-serializable types."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)
