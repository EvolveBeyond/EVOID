"""@controller Syntax — Class-based routes, IOP underneath.

IOP: Decorators auto-create Intents from route path + method.
User just writes @GET("/path") — Intent is created automatically.

Extend support:
  before("GET:/users/{id}", "log_request")
  after("GET:/users/{id}", "log_response")
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from ..core import Context, register, register_processor
from ..core.extend import (
    after as _after,
)
from ..core.extend import (
    after_processor as _after_processor,
)
from ..core.extend import (
    before as _before,
)
from ..core.extend import (
    before_processor as _before_processor,
)
from ..core.extend import (
    replace_pipeline as _replace_pipeline,
)
from ..core.intent import Intent
from ._shared import create_intent as _create_intent

# Handler type
Handler = Callable[..., Awaitable[Any]]


@dataclass
class App:
    """App — pure data (name).

    This is a name container for @controller syntax. The real execution
    happens in the adapter layer (ASGI/Robyn) which converts HTTP
    requests to Intents and routes them through the pipeline.
    """

    name: str


# Alias: README and user code import as "Service"
Service = App


def Controller(prefix: str = "", level: str = "standard") -> Callable:
    """Controller decorator — auto-creates Intents for all routes."""
    def decorator(cls: type) -> type:
        for attr_name in dir(cls):
            if attr_name.startswith("_"):
                continue

            attr = getattr(cls, attr_name)
            if not callable(attr):
                continue

            if hasattr(attr, "_evoid_routes"):
                for route_info in attr._evoid_routes:
                    method = route_info["method"]
                    route_path = route_info["path"]
                    route_level = route_info.get("level", level)

                    full_path = prefix + route_path if prefix else route_path

                    intent = _create_intent(method, full_path, route_level)
                    register(intent)

                    instance = cls()
                    original_method = getattr(instance, attr_name)

                    async def processor(ctx: Context, m=original_method) -> Any:
                        body = ctx.metadata.get("body", {})
                        return await m(**body) if body else await m()

                    register_processor(intent.name, processor)

        return cls
    return decorator


def GET(path: str = "", level: str = "standard") -> Callable:
    """GET method decorator."""
    def decorator(func: Handler) -> Handler:
        if not hasattr(func, "_evoid_routes"):
            func._evoid_routes = []
        func._evoid_routes.append({"method": "GET", "path": path, "level": level})
        return func
    return decorator


def POST(path: str = "", level: str = "standard") -> Callable:
    """POST method decorator."""
    def decorator(func: Handler) -> Handler:
        if not hasattr(func, "_evoid_routes"):
            func._evoid_routes = []
        func._evoid_routes.append({"method": "POST", "path": path, "level": level})
        return func
    return decorator


def PUT(path: str = "", level: str = "standard") -> Callable:
    """PUT method decorator."""
    def decorator(func: Handler) -> Handler:
        if not hasattr(func, "_evoid_routes"):
            func._evoid_routes = []
        func._evoid_routes.append({"method": "PUT", "path": path, "level": level})
        return func
    return decorator


def DELETE(path: str = "", level: str = "standard") -> Callable:
    """DELETE method decorator."""
    def decorator(func: Handler) -> Handler:
        if not hasattr(func, "_evoid_routes"):
            func._evoid_routes = []
        func._evoid_routes.append({"method": "DELETE", "path": path, "level": level})
        return func
    return decorator


# ============================================================
# Extend support for @controller syntax
# ============================================================

def before(route: str, processor: str) -> None:
    """Add processor BEFORE route handler."""
    _before(route, processor)


def after(route: str, processor: str) -> None:
    """Add processor AFTER route handler."""
    _after(route, processor)


def before_handler(route: str, target: str, processor: str) -> None:
    """Add processor BEFORE specific processor."""
    _before_processor(route, target, processor)


def after_handler(route: str, target: str, processor: str) -> None:
    """Add processor AFTER specific processor."""
    _after_processor(route, target, processor)


def replace_pipeline(route: str, processors: list[str]) -> None:
    """Replace entire pipeline for a route."""
    _replace_pipeline(route, processors)


async def run(app: App, host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the @controller app."""
    from ..adapters.asgi import create_app

    asgi_app = create_app(name=app.name)

    import uvicorn
    print(f"Starting {app.name} on http://{host}:{port}")
    uvicorn.run(asgi_app, host=host, port=port)
