---
title: 'Dependency Injection Patterns'
description: 'Manage dependencies in EVOID without a DI container.'
---

# Dependency Injection Patterns

Manage dependencies in EVOID without a DI container.

EVOID doesn't need a DI container. Python's module system and the pipeline's Context provide clean dependency management.

## Module-Level Singletons

For simple apps, import services directly. Python's module system ensures each import resolves to one instance:

```python
from evoid.web.route import Service, get

app = Service("api")

# db is a module-level singleton — import it anywhere
from services import db

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    user = await db.get_user(user_id)
    return {"id": user.id, "name": user.name}
```

```python
# services.py
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["my_app"]
```

!!! tip "When to use"
    Singletons work well for services that hold connections (databases, caches, HTTP clients). Keep one module per service.

## Class-Based Services

For medium apps, wrap dependencies in classes. Instantiate once, import the instance:

```python
from evoid.web.route import Service, get

app = Service("api")

from services.email import email_service

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    user = await db.get_user(user_id)
    return {"id": user.id, "email": user.email}

@post("/users/{user_id}/send-welcome")
async def send_welcome(user_id: int) -> dict:
    user = await db.get_user(user_id)
    await email_service.send_welcome(user.email)
    return {"status": "sent"}
```

```python
# services/email.py
class EmailService:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def send_welcome(self, to: str) -> None:
        await self.client.post(f"{self.base_url}/send", ...)

# Singleton instance
email_service = EmailService(
    api_key=os.environ["EMAIL_API_KEY"],
    base_url="https://api.email.service",
)
```

!!! info "No magic required"
    The class is just a Python class. No decorators, no injection framework, no container — just imports.

## Factory Functions for Testing

Replace dependencies by importing a factory that builds fresh instances:

```python
# services/email.py
def create_email_service(api_key: str = None) -> EmailService:
    return EmailService(
        api_key=api_key or os.environ["EMAIL_API_KEY"],
        base_url=os.environ.get("EMAIL_BASE_URL", "https://api.email.service"),
    )

# Production singleton
email_service = create_email_service()
```

```python
# test_welcome.py
from services.email import create_email_service
from unittest.mock import AsyncMock

# Replace with a mock
email_service = create_email_service(api_key="test-key")
email_service.send = AsyncMock()

# Pass to your test — no global state pollution
```

!!! tip "Testing pattern"
    Factories let tests swap implementations without monkey-patching. Keep the production singleton in the module, expose the factory for tests.

## Using ctx.deps for Per-Request Dependencies

Pass per-request dependencies through the Context object:

```python
from evoid.core import Context

async def inject_db(ctx: Context) -> dict:
    """Create a fresh DB session per request."""
    ctx.deps["db"] = create_session()
    return {"deps_injected": True}

async def handle_request(ctx: Context) -> dict:
    db = ctx.deps["db"]
    users = await db.query("SELECT * FROM users")
    return {"users": users}
```

Register `inject_db` as a pipeline processor so every request gets its own session:

```python
from evoid import register_processor
from evoid.core.extend import before

register_processor("inject_db", inject_db)

before("POST:/users", "inject_db")
before("GET:/users/{id}", "inject_db")
```

!!! warning "ctx.deps lifecycle"
    Dependencies in `ctx.deps` exist for the lifetime of one pipeline execution. They are not shared between requests.

## Using ctx.state for Shared State Between Processors

Share data between processors via `ctx.state` — the pipeline's shared memory:

```python
from evoid.core import Context
from evoid import register_processor

async def fetch_user(ctx: Context) -> dict:
    """Processor 1: fetch the user."""
    user_id = ctx.intent.metadata.get("user_id")
    ctx.state["user"] = await db.get_user(user_id)
    return {"fetched": True}

async def check_permissions(ctx: Context) -> dict:
    """Processor 2: read what processor 1 wrote."""
    user = ctx.state["user"]
    if user.role != "admin":
        raise PermissionError("Admin access required")
    return {"authorized": True}

register_processor("fetch_user", fetch_user)
register_processor("check_permissions", check_permissions)
```

!!! info "ctx.state vs ctx.deps"
    `ctx.state` holds shared data between processors. `ctx.deps` holds service instances injected for the request. Use state for data flow, deps for services.

## @route Style

```python
from evoid.web.route import Service, get, post, before

app = Service("api")

before("POST:/orders", "inject_db")
before("GET:/orders/{id}", "inject_db")

@get("/orders/{id}")
async def get_order(id: int) -> dict:
    db = ctx.deps["db"]  # Available in handler via ctx
    return {"id": id}

@post("/orders")
async def create_order(item_id: int, quantity: int) -> dict:
    return {"status": "created", "item_id": item_id}
```

## @controller Style

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("api")

@Controller("/orders")
class OrderController:
    @GET("/{order_id}")
    async def get_order(self, order_id: int) -> dict:
        return {"id": order_id}

    @POST("/")
    async def create_order(self, item_id: int, quantity: int) -> dict:
        return {"status": "created"}
```

## Native IOP Style

```python
from evoid import Intent, Level, add_intent
from evoid.core import Context

GET_ORDER = Intent(
    name="get_order",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/orders/{id}"},
)

async def handle_get_order(intent: Intent) -> dict:
    order_id = intent.metadata.get("id")
    return {"id": order_id}

add_intent(GET_ORDER, handle_get_order)
```

## Summary

| Pattern | Best For | Mechanism |
|---------|----------|-----------|
| Module singleton | Connection pools, HTTP clients | Python imports |
| Class-based service | Services with config | Import the instance |
| Factory function | Testing | Expose `create_*()` function |
| ctx.deps | Per-request services | Pipeline processor injects |
| ctx.state | Sharing data between processors | Write in one, read in next |
