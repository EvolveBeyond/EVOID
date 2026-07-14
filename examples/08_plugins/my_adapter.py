"""Custom Adapter Plugin — Example of registering your own adapter.

This shows how users can create and register custom adapters.
The adapter converts external events into Intents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from evoid.core.intent import Intent, Level
from evoid.engines.plugin.registry import register


# ============================================================
# 1. Define your adapter as pure data + functions
# ============================================================

@dataclass
class MyCustomAdapter:
    """Your custom adapter — just data."""

    name: str
    config: dict[str, Any] = field(default_factory=dict)
    _handlers: dict[str, Callable] = field(default_factory=dict)

    def on(self, event: str, handler: Callable) -> None:
        """Register event handler."""
        self._handlers[event] = handler


def create_adapter(name: str = "custom", **config: Any) -> MyCustomAdapter:
    """Create your custom adapter."""
    return MyCustomAdapter(name=name, config=config)


async def handle_event(adapter: MyCustomAdapter, event: str, data: Any) -> Intent:
    """Convert external event to Intent."""
    return Intent(
        name=f"custom:{event}",
        level=Level.STANDARD,
        metadata={"data": data, "adapter": adapter.name},
    )


# ============================================================
# 2. Register as a plugin
# ============================================================

def register_plugin():
    """Called by plugin loader to register this adapter."""
    return register(
        name="my-custom-adapter",
        type="adapter",
        factory=create_adapter,
        version="1.0.0",
        description="My custom adapter for special protocol",
        author="Me",
        dependencies=(),
    )


# Auto-register when imported
register_plugin()
