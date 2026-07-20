---
title: 'Streaming Responses'
description: 'Handle streaming, SSE, and WebSocket in your adapter.'
---

# Streaming Responses

EVOID's runtime processes intents synchronously — one input, one result. Streaming (SSE, WebSocket, chunked responses) requires adapter-level handling. The runtime doesn't know about streams, but your adapter can bridge them.

## Server-Sent Events (SSE)

For SSE, your adapter creates a streaming response and yields events:

```python
import asyncio
import json
from starlette.requests import Request
from starlette.responses import StreamingResponse
from evoid.core import Intent, Level, execute


async def handle_sse(request: Request) -> StreamingResponse:
    intent = Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={"method": request.method, "path": request.url.path},
    )

    async def event_generator():
        # Execute intent — processor produces a list of events
        result = await execute(intent)

        if not result.success:
            yield f"data: {json.dumps({'error': str(result.error)})}\n\n"
            return

        # Yield each event as SSE
        events = result.value if isinstance(result.value, list) else [result.value]
        for event in events:
            yield f"data: {json.dumps(event)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

!!! info "Streaming is adapter-level"
    The runtime returns a `Result` with a complete value. Your adapter decides how to stream it. For SSE, the adapter wraps the result in a `StreamingResponse`.

## WebSocket Adapter

For WebSocket connections, the adapter manages the connection lifecycle:

```python
from starlette.websockets import WebSocket, WebSocketDisconnect
from evoid.core import Intent, Level, execute


async def handle_websocket(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            # Convert to intent
            intent = Intent(
                name="ws:message",
                level=Level.STANDARD,
                metadata={
                    "action": data.get("action"),
                    "payload": data.get("payload"),
                },
            )

            # Execute
            result = await execute(intent)

            # Send response
            if result.success:
                await websocket.send_json({"status": "ok", "data": result.value})
            else:
                await websocket.send_json({"status": "error", "error": str(result.error)})

    except WebSocketDisconnect:
        pass
```

!!! tip "WebSocket adapters manage state"
    Unlike HTTP (stateless per request), WebSocket adapters maintain a connection. Your adapter handles accept/receive/send — the runtime only sees intents.

## Processor Yielding Events

Processors can produce lists for the adapter to stream:

```python
from evoid.core import Context


async def stream_data(ctx: Context) -> list[dict]:
    # Simulate producing events over time
    events = []
    for i in range(10):
        events.append({"index": i, "value": f"event_{i}"})
    return events
```

## @route Style with Streaming

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service

app = Service("api")

@get("/events")
async def get_events() -> list[dict]:
    return [{"event": "connected"}, {"event": "data", "value": 42}]
```

The adapter wraps the result in a `StreamingResponse` at the entry point.

## @controller Style

```python
from evoid.web.controller import Service, Controller, GET

app = Service("api")

@Controller("/stream")
class StreamController:
    @GET("/events")
    async def events(self) -> list[dict]:
        return [{"event": "connected"}, {"event": "data", "value": 42}]
```

## Native IOP Style

```python
from evoid import Intent, Level, add_intent

STREAM_EVENTS = Intent(
    name="get:events",
    level=Level.STANDARD,
)


async def handle_stream_events(intent: Intent) -> list[dict]:
    return [{"event": "connected"}, {"event": "data", "value": 42}]


add_intent(STREAM_EVENTS, handle_stream_events)
```

## Complete SSE Adapter

A full adapter that routes SSE and regular requests:

```python
import json
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from evoid.core import Intent, Level, execute


async def handle_sse(request: Request) -> StreamingResponse:
    async def generate():
        result = await execute(Intent(
            name="sse:stream",
            level=Level.STANDARD,
            metadata={"headers": dict(request.headers)},
        ))
        if result.success:
            for event in result.value:
                yield f"data: {json.dumps(event)}\n\n"
        else:
            yield f"data: {json.dumps({'error': str(result.error)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


async def handle_api(request: Request) -> JSONResponse:
    body = await request.body() if request.method in ("POST", "PUT") else b"{}"
    intent = Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={"body": json.loads(body) if body else {}},
    )
    result = await execute(intent)
    if result.success:
        return JSONResponse(result.value)
    return JSONResponse({"error": str(result.error)}, status_code=500)


app = Starlette(routes=[
    Route("/events", handle_sse, methods=["GET"]),
    Route("/api/{path:path}", handle_api, methods=["GET", "POST", "PUT", "DELETE"]),
])
```

!!! tip "Streaming is your adapter's job"
    The runtime returns complete results. Your adapter decides whether to stream them. This keeps the runtime simple and the adapter flexible for any protocol.
