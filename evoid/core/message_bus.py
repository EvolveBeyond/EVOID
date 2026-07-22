"""Message Bus — Intent-based inter-service communication.

IOP: Services communicate through Intents, not HTTP.
When services run on the same system, they share a message bus.
No HTTP overhead. Intent-based routing.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from .intent import Intent

# Message types
Handler = Callable[[Intent], Awaitable[Any]]

# Max history size — prevents unbounded memory growth
_MAX_HISTORY = 1000

# Thread lock for global state mutations
_lock = threading.Lock()


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

# Global message history for debugging — capped
_history: list[Message] = []


def subscribe(topic: str, handler: Handler) -> None:
    """Subscribe to a topic.

    Topics can be:
    - Intent name (e.g., "process_payment")
    - Level (e.g., "critical")
    - Wildcard ("*")
    """
    with _lock:
        _subscriptions.setdefault(topic, []).append(handler)


def unsubscribe(topic: str, handler: Handler) -> bool:
    """Unsubscribe from a topic."""
    with _lock:
        if topic in _subscriptions:
            try:
                _subscriptions[topic].remove(handler)
                return True
            except ValueError:
                pass
        return False


async def publish(intent: Intent | str, source: str = "", target: str = "") -> list[Any]:
    """Publish an intent to all matching subscribers.

    Args:
        intent: Intent object or topic string. String is auto-wrapped in Intent.
        source: Source identifier.
        target: Target identifier.
    """
    # Accept string topic — auto-wrap in Intent
    if isinstance(intent, str):
        from .intent import Level
        intent = Intent(name=intent, level=Level.STANDARD)

    message = Message(intent=intent, source=source, target=target)
    with _lock:
        if len(_history) < _MAX_HISTORY:
            _history.append(message)

    # Find matching handlers
    handlers = _find_handlers(intent)

    if not handlers:
        return []

    # Execute all handlers concurrently
    tasks = [handler(intent) for handler in handlers]
    return list(await asyncio.gather(*tasks, return_exceptions=True))


def _find_handlers(intent: Intent) -> list[Handler]:
    """Find handlers matching an intent."""
    handlers: list[Handler] = []

    # Exact intent name match
    subs = _subscriptions.get(intent.name)
    if subs:
        handlers.extend(subs)

    # Level match
    subs = _subscriptions.get(intent.level.value)
    if subs:
        handlers.extend(subs)

    # Wildcard match
    subs = _subscriptions.get("*")
    if subs:
        handlers.extend(subs)

    return handlers


def get_history() -> list[Message]:
    """Get message history."""
    return list(_history)


def clear_history() -> None:
    """Clear message history."""
    _history.clear()


def clear_all() -> None:
    """Clear all subscriptions and history."""
    _subscriptions.clear()
    _history.clear()
