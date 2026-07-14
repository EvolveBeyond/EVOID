"""Robyn Adapter — Converts Robyn requests to Intents.

IOP: Adapter is just functions. No class with behavior.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from ..core.intent import Intent, Level
from ..core.runtime import execute


# Handler type
Handler = Callable[[Intent], Awaitable[Any]]


@dataclass
class RobynApp:
    """Robyn app — pure data (name + handlers + routes)."""

    name: str
    handlers: dict[str, Handler] = field(default_factory=dict)
    routes: list[dict[str, Any]] = field(default_factory=list)


def create_app(name: str = "evoid-robyn") -> RobynApp:
    """Create a Robyn application."""
    return RobynApp(name=name)


def route(app: RobynApp, method: str, path: str, handler: Handler) -> None:
    """Register a route handler."""
    key = f"{method.upper()}:{path}"
    app.handlers[key] = handler
    app.routes.append({"method": method.upper(), "path": path, "handler": handler})


def get(app: RobynApp, path: str) -> Callable:
    """Decorator to register GET handler."""
    def decorator(func: Handler):
        route(app, "GET", path, func)
        return func
    return decorator


def post(app: RobynApp, path: str) -> Callable:
    """Decorator to register POST handler."""
    def decorator(func: Handler):
        route(app, "POST", path, func)
        return func
    return decorator


def _intent_from_request(
    method: str,
    path: str,
    body: bytes,
    headers: dict[str, str],
    query_params: dict[str, str] | None = None,
) -> Intent:
    """Convert request to Intent."""
    data = {}
    if body:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"raw": body.decode("utf-8", errors="replace")}

    level = Level.STANDARD
    intent_header = headers.get("x-intent-level", "").lower()
    if intent_header == "critical":
        level = Level.CRITICAL
    elif intent_header == "ephemeral":
        level = Level.EPHEMERAL

    return Intent(
        name=f"{method.upper()}:{path}",
        level=level,
        metadata={
            "method": method,
            "path": path,
            "body": data,
            "headers": headers,
            "query_params": query_params or {},
        },
    )


async def handle_request(
    app: RobynApp,
    method: str,
    path: str,
    body: bytes,
    headers: dict[str, str],
    query_params: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Handle a request."""
    intent = _intent_from_request(method, path, body, headers, query_params)

    key = f"{method.upper()}:{path}"
    handler = app.handlers.get(key)

    try:
        if handler:
            result = await handler(intent)
        else:
            pipeline_result = await execute(intent)
            if pipeline_result.success:
                result = pipeline_result.value
            else:
                return {"error": str(pipeline_result.error)}

        return {
            "status": "success",
            "intent": intent.name,
            "result": result,
        }

    except Exception as e:
        return {"error": str(e)}


def run_app(
    app: RobynApp,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> None:
    """Run the Robyn application."""
    try:
        from robyn import Robyn, Request, Response
    except ImportError:
        raise ImportError("robyn required: pip install robyn")

    robyn_app = Robyn()

    for route_info in app.routes:
        method = route_info["method"]
        path = route_info["path"]
        handler = route_info["handler"]

        async def make_handler(h, m, p):
            async def route_handler(request: Request) -> Response:
                body = request.body if hasattr(request, "body") else b""
                headers = dict(request.headers) if hasattr(request, "headers") else {}
                query = dict(request.query_params) if hasattr(request, "query_params") else {}

                result = await handle_request(app, m, p, body, headers, query)

                if isinstance(result, tuple):
                    data, status = result
                else:
                    data = result
                    status = 200

                return Response(
                    status_code=status,
                    headers={"Content-Type": "application/json"},
                    description=json.dumps(data),
                )
            return route_handler

        robyn_app.add_route(method, path, make_handler(handler, method, path))

    print(f"Starting {app.name} on http://{host}:{port}")
    robyn_app.start(host=host, port=port)
