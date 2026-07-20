---
title: 'CORS'
description: 'Add CORS support to your EVOID application.'
---

# CORS

CORS is an HTTP concern — EVOID handles it in the adapter layer. You have two approaches: middleware in the adapter, or a processor that adds CORS headers.

## Approach 1: Middleware in the Adapter

The simplest approach — add CORS middleware to your Starlette app:

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route

from evoid.core import Intent, execute


async def handle(request):
    intent = Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={"method": request.method, "path": request.url.path},
    )
    result = await execute(intent)
    if result.success:
        from starlette.responses import JSONResponse
        return JSONResponse(result.value)
    from starlette.responses import JSONResponse
    return JSONResponse({"error": str(result.error)}, status_code=500)


app = Starlette(
    routes=[Route("/{path:path}", handle, methods=["GET", "POST", "PUT", "DELETE"])],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
)
```

!!! info "Middleware runs before intent creation"
    CORSMiddleware handles preflight OPTIONS requests and adds headers before your adapter code runs. This is the cleanest approach for simple CORS policies.

## Approach 2: Processor-Based CORS

For dynamic CORS policies (e.g., allow different origins per route), use a processor:

```python
from evoid.core import Context


ALLOWED_ORIGINS = {
    "GET:/users": ["https://app.example.com"],
    "POST:/users": ["https://admin.example.com"],
    "*": ["https://any.example.com"],
}


async def cors_processor(ctx: Context) -> dict:
    method = ctx.metadata.get("method", "")
    path = ctx.metadata.get("path", "")
    headers = ctx.metadata.get("headers", {})
    origin = headers.get("origin", "")

    # Find matching CORS policy
    allowed = ALLOWED_ORIGINS.get(f"{method}:{path}")
    if allowed is None:
        allowed = ALLOWED_ORIGINS.get("*", [])

    if origin in allowed:
        ctx.state["cors_headers"] = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    else:
        ctx.state["cors_headers"] = {}

    return {"cors_configured": True}
```

!!! tip "Use middleware for simple cases"
    Processor-based CORS is more flexible but adds complexity. Use Starlette middleware unless you need per-route policies.

## Attaching CORS Headers to Responses

If using the processor approach, you need an `after` processor to attach headers:

```python
from evoid.core import Context
from evoid.adapters.asgi import get
from evoid.web.route import Service, before, after

app = Service("api")

@get("/users")
async def get_users() -> dict:
    return {"users": []}

before("GET:/users", "cors_processor")
after("GET:/users", "attach_cors_headers")
```

```python
from starlette.responses import JSONResponse


async def attach_cors_headers(ctx: Context) -> dict:
    cors = ctx.state.get("cors_headers", {})
    # Store headers for the adapter to include in response
    ctx.state["response_headers"] = cors
    return ctx.state.get("last_result", {})
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

from evoid.web.controller import before
before("GET:/data/", "cors_processor")
```

## Native IOP Style

```python
from evoid import Intent, Level, add_intent

GET_DATA = Intent(
    name="get:data",
    level=Level.STANDARD,
)


async def handle_get_data(intent: Intent) -> dict:
    return {"data": [1, 2, 3]}


add_intent(GET_DATA, handle_get_data)
```

## Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Middleware | Simple, handles preflight, battle-tested | Fixed policy, runs on every request |
| Processor | Dynamic per-route, integrates with pipeline | More complex, manual preflight handling |

!!! tip "Start with middleware"
    Use Starlette CORSMiddleware unless you specifically need per-route dynamic policies. It handles edge cases (preflight caching, Vary headers) that are easy to get wrong.
