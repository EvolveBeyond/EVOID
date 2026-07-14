"""Message Bus — Intent-based inter-service communication.

IOP: Services communicate through Intents, not HTTP.
When services run on the same system, they share a message bus.
No HTTP overhead. Intent-based routing.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from .intent import Intent, Level


# Message types
Handler = Callable[[Intent], Awaitable[Any]]


@dataclass(frozen=True)
class Message:
    """Intent-based message — pure data."""

    intent: Intent
    source: str = ""
    target: str = ""
    reply_to: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# Global subscriptions: topic -> list of handlers
_subscriptions: dict[str, list[Handler]] = {}

# Global message history for debugging
_history: list[Message] = []


def subscribe(topic: str, handler: Handler) -> None:
    """Subscribe to a topic.

    Topics can be:
    - Intent name (e.g., "process_payment")
    - Level (e.g., "critical")
    - Wildcard ("*")
    """
    _subscriptions.setdefault(topic, []).append(handler)


def unsubscribe(topic: str, handler: Handler) -> bool:
    """Unsubscribe from a topic."""
    if topic in _subscriptions:
        try:
            _subscriptions[topic].remove(handler)
            return True
        except ValueError:
            pass
    return False


async def publish(intent: Intent, source: str = "", target: str = "") -> list[Any]:
    """Publish an intent to all matching subscribers.

    This is the core communication function.
    No HTTP. No serialization. Direct function calls.
    """
    message = Message(intent=intent, source=source, target=target)
    _history.append(message)

    results = []

    # Find matching handlers
    handlers = _find_handlers(intent)

    # Execute all handlers concurrently
    if handlers:
        tasks = [handler(intent) for handler in handlers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    return results


def _find_handlers(intent: Intent) -> list[Handler]:
    """Find handlers matching an intent."""
    handlers: list[Handler] = []

    # Exact intent name match
    if intent.name in _subscriptions:
        handlers.extend(_subscriptions[intent.name])

    # Level match
    if intent.level.value in _subscriptions:
        handlers.extend(_subscriptions[intent.level.value])

    # Wildcard match
    if "*" in _subscriptions:
        handlers.extend(_subscriptions["*"])

    return handlers


def get_history() -> list[Message]:
    """Get message history."""
    return _history.copy()


def clear_history() -> None:
    """Clear message history."""
    _history.clear()


def clear_all() -> None:
    """Clear all subscriptions and history."""
    _subscriptions.clear()
    _history.clear()
