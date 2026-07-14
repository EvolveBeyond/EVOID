"""@route Syntax — Function-based routes, IOP underneath.

IOP: Decorators auto-create Intents from route path + method.
User just writes @get("/path") — Intent is created automatically.

Extend support:
  before("GET:/users/{id}", "log_request")
  after("GET:/users/{id}", "log_response")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from ..core.intent import Intent, Level
from ..core import register, register_processor, Context
from ..core.extend import (
    before as _before,
    after as _after,
    before_processor as _before_processor,
    after_processor as _after_processor,
    replace_pipeline as _replace_pipeline,
)


# Handler type
Handler = Callable[..., Awaitable[Any]]


@dataclass
class App:
    """App — pure data (name)."""

    name: str


def Service(name: str) -> App:
    """Create a service (like FastAPI())."""
    return App(name=name)


def _create_intent(method: str, path: str, level: str = "standard") -> Intent:
    """Auto-create Intent from method + path."""
    intent_level = Level(level) if level in ("ephemeral", "standard", "critical") else Level.STANDARD

    return Intent(
        name=f"{method.upper()}:{path}",
        level=intent_level,
        metadata={"method": method, "path": path},
    )


def get(path: str, level: str = "standard") -> Callable:
    """GET endpoint — auto-creates Intent."""
    def decorator(func: Handler) -> Handler:
        intent = _create_intent("GET", path, level)
        register(intent)

        async def processor(ctx: Context) -> Any:
            params = ctx.metadata.get("params", {})
            return await func(**params)

        register_processor(intent.name, processor)
        func._evoid_intent = intent
        return func
    return decorator


def post(path: str, level: str = "standard") -> Callable:
    """POST endpoint — auto-creates Intent."""
    def decorator(func: Handler) -> Handler:
        intent = _create_intent("POST", path, level)
        register(intent)

        async def processor(ctx: Context) -> Any:
            body = ctx.metadata.get("body", {})
            return await func(**body)

        register_processor(intent.name, processor)
        func._evoid_intent = intent
        return func
    return decorator


def put(path: str, level: str = "standard") -> Callable:
    """PUT endpoint — auto-creates Intent."""
    def decorator(func: Handler) -> Handler:
        intent = _create_intent("PUT", path, level)
        register(intent)

        async def processor(ctx: Context) -> Any:
            body = ctx.metadata.get("body", {})
            return await func(**body)

        register_processor(intent.name, processor)
        func._evoid_intent = intent
        return func
    return decorator


def delete(path: str, level: str = "standard") -> Callable:
    """DELETE endpoint — auto-creates Intent."""
    def decorator(func: Handler) -> Handler:
        intent = _create_intent("DELETE", path, level)
        register(intent)

        async def processor(ctx: Context) -> Any:
            params = ctx.metadata.get("params", {})
            return await func(**params)

        register_processor(intent.name, processor)
        func._evoid_intent = intent
        return func
    return decorator


# ============================================================
# Extend support for @route syntax
# ============================================================

def before(route: str, processor: str) -> None:
    """Add processor BEFORE route handler.

    Usage:
        before("GET:/users/{id}", "log_request")
    """
    _before(route, processor)


def after(route: str, processor: str) -> None:
    """Add processor AFTER route handler.

    Usage:
        after("GET:/users/{id}", "log_response")
    """
    _after(route, processor)


def before_handler(route: str, target: str, processor: str) -> None:
    """Add processor BEFORE specific processor in route.

    Usage:
        before_handler("GET:/users/{id}", "authorize", "check_permission")
    """
    _before_processor(route, target, processor)


def after_handler(route: str, target: str, processor: str) -> None:
    """Add processor AFTER specific processor in route.

    Usage:
        after_handler("GET:/users/{id}", "validate", "enrich_data")
    """
    _after_processor(route, target, processor)


def replace_pipeline(route: str, processors: list[str]) -> None:
    """Replace entire pipeline for a route.

    Usage:
        replace_pipeline("GET:/users/{id}", ["cache", "fetch", "log"])
    """
    _replace_pipeline(route, processors)


async def run(app: App, host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the @route app."""
    from ..adapters.asgi import create_app

    asgi_app = create_app(name=app.name)

    import uvicorn
    print(f"Starting {app.name} on http://{host}:{port}")
    uvicorn.run(asgi_app, host=host, port=port)
