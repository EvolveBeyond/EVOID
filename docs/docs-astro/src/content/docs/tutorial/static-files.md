---
title: 'Static Files'
description: 'Serve static files alongside EVOID intents.'
---

# Static Files

Serving static files is an HTTP concern — it belongs in the adapter. EVOID's runtime only handles intents, so you mount static file serving alongside your EVOID routes.

## Mounting Static Files in Starlette

Use Starlette's `StaticFiles` to serve a directory:

```python
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from evoid.core import Intent, execute


async def handle(request):
    intent = Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={"method": request.method, "path": request.url.path},
    )
    result = await execute(intent)
    if result.success:
        return JSONResponse(result.value)
    return JSONResponse({"error": str(result.error)}, status_code=500)


app = Starlette(
    routes=[
        # EVOID intent routes
        Route("/api/{path:path}", handle, methods=["GET", "POST", "PUT", "DELETE"]),

        # Static files — mounted at /static
        Mount("/static", app=StaticFiles(directory="public"), name="static"),
    ],
)
```

!!! info "Static files bypass the runtime"
    Static file requests never reach `execute()`. Starlette serves them directly — no Intent, no pipeline, no processors. This is correct: static files aren't intents.

## Path Ordering Matters

Starlette matches routes in order. Put specific routes before catch-all patterns:

```python
app = Starlette(
    routes=[
        # Specific API routes first
        Route("/api/health", health_endpoint, methods=["GET"]),
        Route("/api/users", users_endpoint, methods=["GET", "POST"]),

        # Static files
        Mount("/static", app=StaticFiles(directory="public"), name="static"),

        # Catch-all EVOID route last
        Route("/api/{path:path}", handle, methods=["GET", "POST", "PUT", "DELETE"]),
    ],
)
```

!!! warning "Route order"
    If you put the catch-all EVOID route first, static file requests will be routed to your adapter instead of `StaticFiles`. Always mount static files before catch-all patterns.

## Serving from Multiple Directories

```python
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles


app = Starlette(
    routes=[
        # CSS/JS assets
        Mount("/assets", app=StaticFiles(directory="dist/assets"), name="assets"),

        # Uploaded files
        Mount("/uploads", app=StaticFiles(directory="uploads"), name="uploads"),

        # EVOID routes
        Route("/api/{path:path}", handle, methods=["GET", "POST", "PUT", "DELETE"]),
    ],
)
```

## Custom Adapter with Static Files

Here is a complete adapter that serves static files alongside EVOID:

```python
import json
from pathlib import Path
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import JSONResponse

from evoid.core import Intent, Level, execute


PUBLIC_DIR = Path("public")
PUBLIC_DIR.mkdir(exist_ok=True)


async def handle_intent(request: Request) -> JSONResponse:
    method = request.method
    path = request.url.path
    body = await request.body() if method in ("POST", "PUT", "PATCH") else b""

    data = {}
    if body:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}

    intent = Intent(
        name=f"{method.lower()}:{path}",
        level=Level.STANDARD,
        metadata={"method": method, "path": path, "body": data, "headers": dict(request.headers)},
    )

    result = await execute(intent)
    if result.success:
        return JSONResponse(result.value)
    return JSONResponse({"error": str(result.error)}, status_code=500)


app = Starlette(
    routes=[
        Mount("/static", app=StaticFiles(directory=str(PUBLIC_DIR)), name="static"),
        Route("/{path:path}", handle_intent, methods=["GET", "POST", "PUT", "DELETE"]),
    ],
)
```

## @route Style

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service, run
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

app = Service("my-api")

@get("/api/data")
async def get_data() -> dict:
    return {"data": [1, 2, 3]}

# The run function creates the ASGI app — you can extend it
# by importing create_app and adding routes directly
```

## @controller Style

```python
from evoid.web.controller import Service, Controller, GET

app = Service("my-api")

@Controller("/api")
class DataController:
    @GET("/data")
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
    return {"data": [1, 2, 3]}


add_intent(GET_DATA, handle_get_data)
```

!!! tip "Static files are adapter-only"
    The runtime doesn't serve files. Your adapter mounts `StaticFiles` alongside EVOID routes. The runtime only handles intents — everything else is your adapter's job.
