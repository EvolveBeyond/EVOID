---
title: 'Cookie Parameters'
description: 'Extract cookies in your adapter and access them from processors.'
---

# Cookie Parameters

EVOID never touches HTTP specifics — cookie extraction happens in your adapter. The runtime only sees `intent.metadata` and `ctx.metadata`, where your adapter places the parsed cookies.

## Extracting Cookies in Your Adapter

Add cookie parsing to your adapter's `intent_from` method:

```python
from http.cookies import SimpleCookie
from evoid.core import Intent, Level


def intent_from_request(method: str, path: str, body: bytes,
                        headers: dict, raw_cookie: str = "") -> Intent:
    # Parse cookies from the Cookie header
    cookies = {}
    if raw_cookie:
        for item in raw_cookie.split(";"):
            key, _, value = item.strip().partition("=")
            cookies[key] = value

    return Intent(
        name=f"{method.lower()}:{path}",
        level=Level.STANDARD,
        metadata={
            "method": method,
            "path": path,
            "body": parse_body(body),
            "headers": headers,
            "cookies": cookies,
        },
    )
```

## Starlette Integration

In a Starlette-based adapter, access cookies directly from the request:

```python
from starlette.requests import Request
from starlette.responses import JSONResponse
from evoid.core import Intent, Level, execute


async def handle(request: Request) -> JSONResponse:
    # Extract cookies
    cookies = dict(request.cookies)

    intent = Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={
            "method": request.method,
            "path": request.url.path,
            "cookies": cookies,
        },
    )

    result = await execute(intent)

    if result.success:
        return JSONResponse(result.value)
    return JSONResponse({"error": str(result.error)}, status_code=500)
```

!!! info "Cookies are adapter-specific"
    The runtime doesn't know what a cookie is. Your adapter extracts them and places them in metadata. Processors read from metadata — they never import HTTP libraries.

## Accessing Cookies in Processors

Once your adapter puts cookies in metadata, processors access them via `ctx.metadata["cookies"]`:

```python
from evoid.core import Context


async def auth_check(ctx: Context) -> dict:
    cookies = ctx.metadata.get("cookies", {})
    session_id = cookies.get("session_id")

    if not session_id:
        raise ValueError("Missing session cookie")

    user = await lookup_session(session_id)
    return {"user": user}


# @route style
from evoid.adapters.asgi import get
from evoid.web.route import Service, before

app = Service("api")

@get("/dashboard")
async def dashboard() -> dict:
    return {"content": "Welcome back!"}

before("GET:/dashboard", "auth_check")
```

## @controller Style

Same pattern with controllers:

```python
from evoid.web.controller import Service, Controller, GET
from evoid.core import Context


async def require_session(ctx: Context) -> dict:
    cookies = ctx.metadata.get("cookies", {})
    if "session_id" not in cookies:
        raise ValueError("Authentication required")
    return {"authenticated": True}


@app = Service("api")

@Controller("/profile")
class ProfileController:
    @GET("/")
    async def get_profile(self) -> dict:
        return {"name": "Alice", "email": "alice@example.com"}

from evoid.web.controller import before
before("GET:/profile/", "require_session")
```

## Native IOP Style

With native IOP, the handler reads cookies directly from the intent:

```python
from evoid import Intent, Level, add_intent

GET_PROFILE = Intent(
    name="get:profile",
    level=Level.STANDARD,
)


async def handle_get_profile(intent: Intent) -> dict:
    cookies = intent.metadata.get("cookies", {})
    session_id = cookies.get("session_id")

    if not session_id:
        raise ValueError("Missing session cookie")

    user = await lookup_session(session_id)
    return {"name": user.name}


add_intent(GET_PROFILE, handle_get_profile)
```

!!! tip "Session management stays in processors"
    Cookie extraction belongs in the adapter. Session validation, authentication, and authorization belong in processors. This separation keeps the runtime framework-agnostic.
