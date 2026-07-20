---
title: 'Header Parameters'
description: 'Extract headers in your adapter and access them from processors.'
---

# Header Parameters

EVOID never touches HTTP headers — extraction happens in your adapter. The runtime sees only the dict your adapter places in `intent.metadata["headers"]`.

## Extracting Headers in Your Adapter

Your adapter converts raw headers into a dict and attaches them to the intent:

```python
from evoid.core import Intent, Level


def intent_from_request(method: str, path: str, body: bytes,
                        headers: dict[str, str]) -> Intent:
    level = Level.STANDARD
    intent_header = headers.get("x-intent-level", "").lower()
    if intent_header == "critical":
        level = Level.CRITICAL
    elif intent_header == "ephemeral":
        level = Level.EPHEMERAL

    return Intent(
        name=f"{method.lower()}:{path}",
        level=level,
        metadata={
            "method": method,
            "path": path,
            "body": parse_body(body),
            "headers": headers,
        },
    )
```

The built-in ASGI adapter already does this — it passes `dict(request.headers)` into the intent metadata.

## Starlette Integration

```python
from starlette.requests import Request
from starlette.responses import JSONResponse
from evoid.core import Intent, execute


async def handle(request: Request) -> JSONResponse:
    headers = dict(request.headers)

    intent = Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={"headers": headers, "method": request.method, "path": request.url.path},
    )

    result = await execute(intent)
    if result.success:
        return JSONResponse(result.value)
    return JSONResponse({"error": str(result.error)}, status_code=500)
```

## Accessing Headers in Processors

Processors read headers from `ctx.metadata["headers"]`:

```python
from evoid.core import Context


async def check_api_key(ctx: Context) -> dict:
    headers = ctx.metadata.get("headers", {})
    api_key = headers.get("x-api-key")

    if not api_key:
        raise ValueError("Missing X-Api-Key header")

    if not validate_api_key(api_key):
        raise ValueError("Invalid API key")

    return {"authenticated": True}


async def rate_limiter(ctx: Context) -> dict:
    headers = ctx.metadata.get("headers", {})
    client_ip = headers.get("x-forwarded-for", "unknown")

    if is_rate_limited(client_ip):
        raise ValueError("Rate limit exceeded")

    return {"rate_limit_ok": True}
```

!!! info "Headers are a dict"
    Your adapter should normalize headers to lowercase keys for consistent access. The ASGI spec lowercases header names — verify your adapter does the same.

## @route Style

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service, before

app = Service("api")

@get("/data")
async def get_data() -> dict:
    return {"data": [1, 2, 3]}

before("GET:/data", "check_api_key")
before("GET:/data", "rate_limiter")
```

## @controller Style

```python
from evoid.web.controller import Service, Controller, GET

app = Service("api")

@Controller("/data")
class DataController:
    @GET("/")
    async def get_data(self) -> dict:
        return {"data": [1, 2, 3]}
```

## Native IOP Style

```python
from evoid import Intent, Level, add_intent

GET_DATA = Intent(
    name="get:data",
    level=Level.STANDARD,
)


async def handle_get_data(intent: Intent) -> dict:
    headers = intent.metadata.get("headers", {})
    api_key = headers.get("x-api-key")

    if not api_key:
        raise ValueError("Missing X-Api-Key header")

    return {"data": [1, 2, 3]}


add_intent(GET_DATA, handle_get_data)
```

!!! tip "Use headers for cross-cutting concerns"
    Headers like `Authorization`, `X-Request-ID`, and `X-API-Key` are perfect for processors that run before your main handler. Use `before()` to attach them to routes.
