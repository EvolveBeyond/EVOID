"""Service — Intent-based service communication.

IOP: Service is just a name + registered handlers.
No class with behavior — just data and functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .intent import Intent
from .message_bus import Handler, publish, subscribe


@dataclass
class Service:
    """Service — pure data (name + handlers dict)."""

    name: str
    handlers: dict[str, Handler] = field(default_factory=dict)
    running: bool = False


def start(service: Service) -> None:
    """Start a service and register handlers with message bus."""
    service.running = True

    # Register all handlers with message bus
    for intent_name, handler in service.handlers.items():
        async def _wrapper(intent: Intent, h: Handler = handler) -> Any:
            return await h(intent)
        subscribe(intent_name, _wrapper)


def stop(service: Service) -> None:
    """Stop a service."""
    service.running = False


def on(service: Service, intent_name: str, handler: Handler) -> None:
    """Register a handler for an intent."""
    service.handlers[intent_name] = handler

    # If service is already running, register with message bus
    if service.running:
        async def _wrapper(intent: Intent, h: Handler = handler) -> Any:
            return await h(intent)
        subscribe(intent_name, _wrapper)


async def call(service: Service, intent: Intent) -> Any:
    """Call another service with an Intent.

    No HTTP. Direct function call through message bus.
    """
    results = await publish(intent, source=service.name)

    for result in results:
        if not isinstance(result, Exception):
            return result

    return None


async def emit(service: Service, intent: Intent) -> list[Any]:
    """Emit an intent to all subscribers (fire-and-forget)."""
    return await publish(intent, source=service.name)
