---
title: 'Custom Adapters'
description: 'Write adapters that connect any framework or protocol to the EVOID runtime.'
---

# Custom Adapters

EVOID is a runtime, not a web framework. The adapter is the only layer that touches HTTP specifics — the runtime itself never sees requests, responses, or protocols. You write adapters for your specific needs.

## The Adapter Contract

Every adapter implements two methods:

```python
from typing import Any, Protocol
from evoid.core import Intent

class Adapter(Protocol):
    def intent_from(self, event: Any) -> Intent: ...
    def response_from(self, result: Any) -> Any: ...
```

`intent_from` converts external data (HTTP request, CLI args, MQTT message) into an `Intent`. `response_from` converts a `Result` back into whatever the external world expects.

## Minimal Starlette Adapter

Here is a complete adapter that wraps any ASGI framework:

```python
import json
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from evoid.core import Intent, Level, execute


def intent_from_request(method: str, path: str, body: bytes, headers: dict) -> Intent:
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

    return Intent(
        name=f"{method.lower()}:{path}",
        level=level,
        metadata={"method": method, "path": path, "body": data, "headers": headers},
    )


async def handle(request: Request) -> JSONResponse:
    method = request.method
    path = request.url.path
    body = await request.body() if method in ("POST", "PUT", "PATCH") else b""
    headers = dict(request.headers)

    intent = intent_from_request(method, path, body, headers)
    result = await execute(intent)

    if result.success:
        return JSONResponse({"status": "success", "result": result.value})
    return JSONResponse({"error": str(result.error)}, status_code=500)


app = Starlette(routes=[Route("/{path:path}", handle, methods=["GET", "POST", "PUT", "DELETE"])])
```

## Using the Protocol Directly

You can also implement the `Adapter` protocol as a class:

```python
from dataclasses import dataclass
from evoid.contracts.adapter import Adapter
from evoid.core import Intent, Level, execute


@dataclass
class HttpAdapter:
    def intent_from(self, event: dict) -> Intent:
        return Intent(
            name=f"{event['method']}:{event['path']}",
            level=Level.STANDARD,
            metadata=event,
        )

    def response_from(self, result: Any) -> dict:
        if result.success:
            return {"status": "ok", "data": result.value}
        return {"status": "error", "error": str(result.error)}
```

!!! info "Protocol vs abstract base"
    EVOID uses Python's `Protocol` for structural typing — your adapter doesn't need to inherit from anything. If it has `intent_from` and `response_from`, it qualifies.

## Registering with the Runtime

The adapter integrates at the entry point. Your app calls the adapter, the adapter calls `execute`:

```python
from evoid.core import Intent, execute

async def run_adapter(adapter, raw_event):
    intent = adapter.intent_from(raw_event)
    result = await execute(intent)
    return adapter.response_from(result)
```

!!! tip "Adapters are user-provided"
    EVOID ships a reference ASGI adapter — not a production one. You write the adapter that fits your deployment: ASGI, WSGI, CLI, message queue, WebSocket, or anything else.

## @route and @controller Style

Both decorator styles auto-create intents — the adapter just needs to pass the request through:

```python
from evoid.adapters.asgi import get, post
from evoid.web.route import Service, run

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}

# The ASGI adapter handles intent creation — you just write handlers
run(app, port=8000)
```

## Native IOP Style

With native IOP, you define intents explicitly and write a handler that the adapter invokes:

```python
from evoid import Intent, Level, add_intent

GET_USER = Intent(
    name="get:user",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/users/{user_id}"},
)

async def handle_get_user(intent: Intent) -> dict:
    user_id = intent.metadata["params"]["user_id"]
    return {"id": user_id, "name": "Alice"}

add_intent(GET_USER, handle_get_user)
```

## What Goes in metadata

Your adapter decides what goes into `intent.metadata`. Common fields:

| Field | Description |
|-------|-------------|
| `method` | HTTP method (GET, POST, etc.) |
| `path` | Request path |
| `body` | Parsed request body |
| `headers` | Request headers as dict |
| `query` | Query parameters |
| `params` | Path parameters |

!!! tip "Metadata is your adapter's contract"
    Processors read from `intent.metadata` and `ctx.metadata`. Your adapter defines what's available there — the runtime doesn't prescribe a structure.
