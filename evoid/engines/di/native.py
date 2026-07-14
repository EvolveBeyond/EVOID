"""Native DI Engine — Simple dict-based dependency container.

IOP: Just a dict. No class hierarchy.
"""

from __future__ import annotations

from typing import Any


# Dependencies: name -> instance
_container: dict[str, Any] = {}


def register(name: str, instance: Any) -> None:
    """Register a dependency."""
    _container[name] = instance


def resolve(name: str) -> Any | None:
    """Resolve a dependency by name."""
    return _container.get(name)


def has(name: str) -> bool:
    """Check if a dependency exists."""
    return name in _container


def clear() -> None:
    """Clear all dependencies."""
    _container.clear()


def all_deps() -> dict[str, Any]:
    """Return all dependencies."""
    return _container.copy()
