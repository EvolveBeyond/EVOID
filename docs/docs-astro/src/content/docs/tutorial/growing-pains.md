---
title: 'Growing Pains'
description: "Sandy's shop is booming. The CLI is not enough. What breaks and how to fix it."
---

# Growing Pains

Sandy's shop is booming. The CLI is not enough. What breaks and how to fix it.

## The Problem

Sandy's sandwich shop is popular. The CLI works for her, but:

- Customers want to order online
- Multiple employees need access
- Orders need to be stored, not just processed
- Data needs validation — wrong prices break everything
- Errors need proper HTTP responses

## What Breaks

### 1. No Type Safety

```python
# This works but crashes at runtime
async def handle_order(intent: Intent) -> dict:
    qty = intent.metadata.get("qty")  # Could be None, string, anything
    total = qty * 8.99  # 💥 TypeError if qty is None
    return {"total": total}
```

### 2. No Structure

```python
# Metadata is a free-for-all — no validation
await execute(ORDER, sandwich="BLT", qty=-5)  # Negative quantity? No error.
await execute(ORDER, sandwich="BLT", qty="abc")  # String? No error.
```

### 3. No Web Interface

The CLI is fine for Sandy, but customers can't use it. They need a website.

### 4. No Dependency Management

Every processor creates its own database connection:

```python
async def handle_order(intent: Intent) -> dict:
    db = create_connection()  # New connection every time!
    # No sharing, no pooling, no cleanup
```

## The Solution: Level 2

This is where Level 2 (TypedDict + @route) comes in:

| Problem | Solution |
|---------|----------|
| No type safety | TypedDict for structured data |
| No validation | Pydantic models + schema engine |
| No web interface | @route syntax for HTTP endpoints |
| No DI | Pipeline injection with `ctx.deps` |

## Preview: Sandy's Online Shop

Here's what Phase 2 looks like:

```python
from evoid.adapters.asgi import get, post
from evoid.web.route import Service

app = Service("sandy-api")

@get("/menu")
async def list_menu() -> dict:
    return {"menu": MENU}

@post("/orders")
async def create_order(sandwich: str, qty: int = 1) -> dict:
    # Typed, validated, automatically extracted from request
    return {"status": "confirmed", "sandwich": sandwich, "qty": qty}
```

The `@get` and `@post` decorators auto-create Intents. Your functions stay clean. The runtime handles HTTP, validation, and routing.

## What Phase 2 Covers

- **Web API** with @route syntax
- **Validation** with Pydantic models
- **Dependency Injection** for database, cache, auth
- **Error Handling** with proper HTTP responses
- **Testing** the API
- **Configuration** for different environments

## What Phase 3 Covers

When Sandy opens 3 more locations:

- **Multiple services** (orders, inventory, analytics)
- **Inter-service communication** via Message Bus
- **Plugin system** for custom engines
- **AI agent** for inventory management
- **Production deployment**

## The Progression

```
Phase 1: Dict + Functions     → Sandy's CLI tool
Phase 2: TypedDict + @route   → Sandy's Online Shop
Phase 3: Dataclass + Native   → Sandy's Franchise
```

Each phase builds on the last. You don't throw away Phase 1 code — you enhance it.

## Next: Going Online

Let's build Sandy's first web endpoint — [Going Online](going-online.md).
