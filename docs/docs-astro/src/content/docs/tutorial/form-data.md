---
title: 'Form Data'
description: 'Parse form data in your adapter and access it from processors.'
---

# Form Data

EVOID never touches HTTP parsing — form data extraction happens in your adapter. The runtime sees only the dict your adapter places in `intent.metadata["form"]`.

## Parsing Form Data in Your Adapter

For URL-encoded forms, parse the body in your adapter:

```python
from urllib.parse import parse_qs
from evoid.core import Intent, Level


def intent_from_form_request(method: str, path: str, body: bytes,
                             headers: dict) -> Intent:
    content_type = headers.get("content-type", "")
    form_data = {}

    if "application/x-www-form-urlencoded" in content_type:
        parsed = parse_qs(body.decode("utf-8"))
        form_data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

    return Intent(
        name=f"{method.lower()}:{path}",
        level=Level.STANDARD,
        metadata={
            "method": method,
            "path": path,
            "form": form_data,
            "headers": headers,
        },
    )
```

## Multipart Form Parsing

For multipart forms (file uploads, complex data), use `python-multipart`:

```python
import json
from evoid.core import Intent, Level


async def intent_from_multipart(request) -> Intent:
    from starlette.datastructures import UploadFile

    form = await request.form()
    form_data = {}
    files = {}

    for key in form:
        value = form[key]
        if isinstance(value, UploadFile):
            files[key] = {
                "filename": value.filename,
                "content_type": value.content_type,
                "size": value.size,
            }
        else:
            form_data[key] = value

    return Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={
            "method": request.method,
            "path": request.url.path,
            "form": form_data,
            "files": files,
            "headers": dict(request.headers),
        },
    )
```

## Starlette Integration

```python
from starlette.requests import Request
from starlette.responses import JSONResponse
from evoid.core import execute


async def handle(request: Request) -> JSONResponse:
    content_type = request.headers.get("content-type", "")

    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        form_data = dict(form)
    elif "application/json" in content_type:
        form_data = await request.json()
    else:
        form_data = {}

    from evoid.core import Intent, Level
    intent = Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={"form": form_data, "headers": dict(request.headers)},
    )

    result = await execute(intent)
    if result.success:
        return JSONResponse(result.value)
    return JSONResponse({"error": str(result.error)}, status_code=500)
```

!!! info "Form data goes in metadata"
    The runtime doesn't know what form data is. Your adapter parses it and places it in `intent.metadata["form"]`. Processors read from there.

## Accessing Form Data in Processors

```python
from evoid.core import Context


async def validate_registration(ctx: Context) -> dict:
    form = ctx.metadata.get("form", {})

    required = ["username", "email", "password"]
    missing = [f for f in required if f not in form]

    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")

    return {"validated": True, "fields": list(form.keys())}


async def create_user(ctx: Context) -> dict:
    form = ctx.metadata.get("form", {})
    return {"status": "created", "username": form["username"]}
```

## @route Style

```python
from evoid.adapters.asgi import post
from evoid.web.route import Service, before

app = Service("api")

@post("/register")
async def register(username: str, email: str, password: str) -> dict:
    return {"status": "created", "username": username}

before("POST:/register", "validate_registration")
```

## @controller Style

```python
from evoid.web.controller import Service, Controller, POST

app = Service("api")

@Controller("/users")
class UserController:
    @POST("/register")
    async def register(self, username: str, email: str, password: str) -> dict:
        return {"status": "created", "username": username}
```

## Native IOP Style

```python
from evoid import Intent, Level, add_intent

REGISTER = Intent(
    name="post:register",
    level=Level.STANDARD,
)


async def handle_register(intent: Intent) -> dict:
    form = intent.metadata.get("form", {})
    username = form.get("username")

    if not username:
        raise ValueError("Username is required")

    return {"status": "created", "username": username}


add_intent(REGISTER, handle_register)
```

!!! tip "Keep parsing in the adapter"
    Form parsing is an HTTP concern. Your adapter handles it — processors work with clean dicts. This keeps the runtime framework-agnostic.
