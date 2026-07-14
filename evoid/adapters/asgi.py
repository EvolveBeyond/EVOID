"""ASGI Adapter — Converts HTTP requests to Intents.

IOP: Adapter is a function that maps data to Intent.
This adapter creates a Starlette/ASGI app that:
1. Receives HTTP request
2. Converts to Intent
3. Executes through pipeline
4. Returns response
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable, Awaitable

from ..core.intent import Intent, Level
from ..core.runtime import execute


# Handler type: takes Intent, returns result
Handler = Callable[[Intent], Awaitable[Any]]


def create_app(
    name: str = "evoid-service",
    handlers: dict[str, Handler] | None = None,
    port: int = 8000,
) -> Any:
    """Create an ASGI application.

    Args:
        name: Service name
        handlers: Intent name → handler function mapping
        port: Server port

    Returns:
        ASGI application (Starlette)
    """
    try:
        from starlette.applications import Starlette
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from starlette.routing import Route
    except ImportError:
        raise ImportError("starlette required for ASGI adapter: pip install starlette")

    _handlers = handlers or {}

    async def health_endpoint(request: Request) -> JSONResponse:
        """Health check endpoint."""
        return JSONResponse({"status": "healthy", "service": name})

    async def intent_endpoint(request: Request) -> JSONResponse:
        """Handle any request as an Intent."""
        start = time.monotonic()

        # Parse request
        method = request.method
        path = request.url.path

        # Read body
        body = b""
        if method in ("POST", "PUT", "PATCH"):
            body = await request.body()

        # Get headers
        headers = dict(request.headers)

        # Convert to Intent
        intent = _intent_from_request(method, path, body, headers)

        # Find handler or use default pipeline
        handler = _handlers.get(intent.name)

        try:
            if handler:
                result = await handler(intent)
            else:
                # Execute through pipeline
                pipeline_result = await execute(intent)
                if pipeline_result.success:
                    result = pipeline_result.value
                else:
                    return JSONResponse(
                        {"error": str(pipeline_result.error)},
                        status_code=500,
                    )

            duration = time.monotonic() - start

            return JSONResponse({
                "status": "success",
                "intent": intent.name,
                "level": intent.level.value,
                "result": result,
                "duration": round(duration, 3),
            })

        except Exception as e:
            return JSONResponse(
                {"error": str(e)},
                status_code=500,
            )

    # Create routes
    routes = [
        Route("/health", health_endpoint, methods=["GET"]),
        Route("/{path:path}", intent_endpoint, methods=["GET", "POST", "PUT", "DELETE", "PATCH"]),
    ]

    return Starlette(routes=routes)


def _intent_from_request(
    method: str,
    path: str,
    body: bytes,
    headers: dict[str, str],
) -> Intent:
    """Convert HTTP request to Intent."""
    # Parse body
    data = {}
    if body:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"raw": body.decode("utf-8", errors="replace")}

    # Determine level from headers
    level = Level.STANDARD
    intent_header = headers.get("x-intent-level", "").lower()
    if intent_header == "critical":
        level = Level.CRITICAL
    elif intent_header == "ephemeral":
        level = Level.EPHEMERAL

    # Create intent name from method + path
    name = f"{method.lower()}:{path}"

    return Intent(
        name=name,
        level=level,
        metadata={
            "method": method,
            "path": path,
            "body": data,
            "headers": headers,
        },
    )


def run(
    name: str = "evoid-service",
    handlers: dict[str, Handler] | None = None,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> None:
    """Run the ASGI server.

    Convenience function to create and run the app.
    """
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn required: pip install uvicorn")

    app = create_app(name=name, handlers=handlers, port=port)
    print(f"Starting {name} on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
