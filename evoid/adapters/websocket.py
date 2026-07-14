"""WebSocket Adapter — Converts WebSocket messages to Intents.

IOP: Adapter is just functions. No class with behavior.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from ..core.intent import Intent, Level
from ..core.runtime import execute


# Handler type
Handler = Callable[[Intent], Awaitable[Any]]


@dataclass
class WebSocketApp:
    """WebSocket app — pure data (name + handlers)."""

    name: str
    handlers: dict[str, Handler] = field(default_factory=dict)


def create_ws_app(name: str = "evoid-ws") -> WebSocketApp:
    """Create a WebSocket application."""
    return WebSocketApp(name=name)


def on(ws_app: WebSocketApp, event_type: str, handler: Handler) -> None:
    """Register handler for event type."""
    ws_app.handlers[event_type] = handler


def _intent_from_ws_message(data: str | bytes, metadata: dict[str, Any] | None = None) -> Intent:
    """Convert WebSocket message to Intent."""
    if isinstance(data, bytes):
        data = data.decode("utf-8")

    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        parsed = {"raw": data}

    if isinstance(parsed, dict) and "intent" in parsed:
        name = parsed["intent"]
        level = Level(parsed.get("level", "standard"))
        meta = parsed.get("metadata", {})
    else:
        name = "ws:message"
        level = Level.STANDARD
        meta = {"data": parsed}

    return Intent(
        name=name,
        level=level,
        metadata={**(metadata or {}), **meta},
    )


def create_asgi_app(ws_app: WebSocketApp) -> Any:
    """Create ASGI app with WebSocket support."""
    try:
        from starlette.applications import Starlette
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from starlette.websockets import WebSocket, WebSocketDisconnect
        from starlette.routing import Route, WebSocketRoute
    except ImportError:
        raise ImportError("starlette required: pip install starlette")

    async def ws_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()

        connect_handler = ws_app.handlers.get("connect")
        if connect_handler:
            intent = Intent(name="ws:connect", level=Level.EPHEMERAL, metadata={})
            await connect_handler(intent)

        try:
            while True:
                data = await websocket.receive_text()
                intent = _intent_from_ws_message(data)

                handler = ws_app.handlers.get("message")
                if handler:
                    result = await handler(intent)
                    if result:
                        await websocket.send_json(result)
                else:
                    pipeline_result = await execute(intent)
                    if pipeline_result.success and pipeline_result.value:
                        await websocket.send_json(pipeline_result.value)

        except WebSocketDisconnect:
            disconnect_handler = ws_app.handlers.get("disconnect")
            if disconnect_handler:
                intent = Intent(name="ws:disconnect", level=Level.EPHEMERAL, metadata={})
                await disconnect_handler(intent)

    async def health_endpoint(request: Request) -> JSONResponse:
        return JSONResponse({"status": "healthy", "service": ws_app.name})

    return Starlette(routes=[
        WebSocketRoute("/ws", ws_endpoint),
        Route("/health", health_endpoint, methods=["GET"]),
    ])
