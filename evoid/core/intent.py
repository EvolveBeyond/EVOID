"""Intent — Pure data. Carries purpose, not behavior.

IOP Principle: Data carries its own intent.
Intent is a frozen dataclass — it IS the data, not a class with methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Level(str, Enum):
    """Intent importance levels.

    EPHEMERAL → temporary, aggressive cache, low priority
    STANDARD  → normal, balanced processing
    CRITICAL  → vital, strong consistency, high priority, emergency buffer
    """

    EPHEMERAL = "ephemeral"
    STANDARD = "standard"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Intent:
    """Immutable declaration of purpose.

    This is DATA, not behavior. The runtime reads this data
    and decides what to do. The Intent never decides for itself.
    """

    name: str
    level: Level = Level.STANDARD
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout: float | None = None
    priority: int = 0


# Type alias for intent name
IntentName = str


# Global registry — just a dict, not a class
_registry: dict[IntentName, Intent] = {}


def register(intent: Intent) -> None:
    """Register an intent definition."""
    _registry[intent.name] = intent


def resolve(name: IntentName) -> Intent | None:
    """Resolve an intent by name."""
    return _registry.get(name)


def all_intents() -> dict[IntentName, Intent]:
    """Return all registered intents."""
    return _registry.copy()


def clear_registry() -> None:
    """Clear all registered intents."""
    _registry.clear()
