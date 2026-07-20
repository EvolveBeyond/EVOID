"""@route Syntax — Function-based routes, re-exported from adapter.

IOP: Route decorators (get, post, put, delete) live in the adapter
layer because param extraction is adapter-specific. This module
re-exports them for convenience.

Primary import:
    from evoid.adapters.asgi import get, post      # explicit adapter
    from evoid.web.route import get, post           # convenience (same thing)

Extend support:
    before("GET:/users/{id}", "log_request")
    after("GET:/users/{id}", "log_response")
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from ..adapters.asgi import delete as delete  # noqa: F811 — re-export from adapter
from ..adapters.asgi import get as get  # noqa: F811 — re-export from adapter
from ..adapters.asgi import post as post  # noqa: F811 — re-export from adapter
from ..adapters.asgi import put as put  # noqa: F811 — re-export from adapter
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

# Handler type
Handler = Callable[..., Awaitable[Any]]


@dataclass
class App:
    """App — pure data (name).

    Name container for @route syntax. The adapter does the real work:
    converts HTTP requests to Intents and routes them through the pipeline.
    """

    name: str


# Alias: README and user code import as "Service"
Service = App


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
    """Run the @route app via ASGI adapter."""
    from ..adapters.asgi import create_app

    asgi_app = create_app(name=app.name)

    import uvicorn
    print(f"Starting {app.name} on http://{host}:{port}")
    uvicorn.run(asgi_app, host=host, port=port)
