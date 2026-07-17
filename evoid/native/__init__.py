"""Native — IOP mother syntax.

The base syntax for ALL Intent-Oriented Programming in EVOID.
Works on ANY adapter: web, CLI, Telegram, WebSocket, MQTT, etc.

Usage:
    from evoid.native import create_service, on

    app = create_service("my-service")
    on(app, Intent(name="hello"), handler)
    await execute_service(app, "hello")

This is NOT web-specific. It's the IOP foundation.
Web features live in evoid.web (route, controller, pipeline).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from ..core import register, register_processor
from ..core.intent import Intent, Level  # noqa: F401 — re-exported for users
from ..core.runtime import execute as _execute

# Handler type: takes Intent, returns result
Handler = Callable[[Intent], Awaitable[Any]]


@dataclass
class Service:
    """Service — pure data (name + intents + handlers).

    This is the IOP-level Service, NOT evoid.core.Service (which is for
    inter-service communication via message bus).
    """

    name: str
    intents: list[Intent] = field(default_factory=list)
    handlers: dict[str, Handler] = field(default_factory=dict)


def create_service(name: str) -> Service:
    """Create a service — IOP mother syntax."""
    return Service(name=name)


def on(service: Service, intent: Intent, handler: Handler) -> None:
    """Register a handler for an intent."""
    service.intents.append(intent)
    service.handlers[intent.name] = handler
    register(intent)
    register_processor(intent.name, handler)


async def execute_service(service: Service, intent_name: str, **kwargs: Any) -> Any:
    """Execute an intent by name."""
    return await _execute(intent_name, **kwargs)


async def run(service: Service, host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the service via auto-detected adapter.

    Auto-detects: FastAPI/Starlette (ASGI) or Robyn.
    For explicit adapter choice, use evoid.native.pipeline directly.
    """
    from .pipeline import create_web_pipeline

    pipeline = create_web_pipeline(service)
    await pipeline.run(host=host, port=port)
