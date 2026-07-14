"""IOP Native Syntax — Intent-first approach.

IOP: Pure Intent system. No sugar. Direct and explicit.

This is the native EVOID syntax for users who want full control.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from ..core.intent import Intent, Level
from ..core import register, register_processor, Context, execute
from ..core.runtime import execute as execute_intent


# Handler type
Handler = Callable[[Intent], Awaitable[Any]]


@dataclass
class Service:
    """Service — pure data (name + intents + handlers)."""

    name: str
    intents: list[Intent] = field(default_factory=list)
    handlers: dict[str, Handler] = field(default_factory=dict)


def create_service(name: str) -> Service:
    """Create a service."""
    return Service(name=name)


def on(service: Service, intent: Intent, handler: Handler) -> None:
    """Register a handler for an intent."""
    service.intents.append(intent)
    service.handlers[intent.name] = handler
    register(intent)
    register_processor(intent.name, handler)


async def execute_service(service: Service, intent_name: str, **kwargs: Any) -> Any:
    """Execute an intent by name."""
    return await execute_intent(intent_name, **kwargs)


async def run(service: Service, host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the IOP service."""
    from ..adapters.asgi import create_app

    handlers = {}
    for intent in service.intents:
        handlers[intent.name] = service.handlers[intent.name]

    asgi_app = create_app(name=service.name, handlers=handlers)

    import uvicorn
    print(f"Starting {service.name} on http://{host}:{port}")
    uvicorn.run(asgi_app, host=host, port=port)
