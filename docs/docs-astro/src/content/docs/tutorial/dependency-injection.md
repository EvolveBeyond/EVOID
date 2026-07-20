---
title: 'Dependency Injection'
description: 'Manage dependencies through the pipeline — data carries what it needs.'
---

# Dependency Injection

Manage dependencies through the pipeline — data carries what it needs.

In IOP, dependencies flow through the pipeline: processors inject into `ctx.deps`, handlers read from it. The Intent declares what it needs, the pipeline provides it.

!!! info "DI = kitchen supplies"
    Think of `ctx.deps` as the kitchen's supply closet. A processor stocks it (injects the database, the cache, the auth provider). The handler grabs what it needs. Each request gets its own closet — no sharing, no conflicts.

## The IOP Way: Pipeline Injection

Define what your Intent needs, then wire it through the pipeline:

```python
from evoid import Intent, Level, add_intent, register_processor
from evoid.core import Context

# Processor: inject DB session into context
async def inject_db(ctx: Context) -> dict:
    ctx.deps["db"] = create_session()
    return {"db_ready": True}

# Handler: reads injected dependency
async def handle_get_user(intent: Intent, ctx: Context) -> dict:
    user_id = intent.metadata.get("user_id")
    db = ctx.deps["db"]
    user = await db.get_user(user_id)
    return {"id": user.id, "name": user.name}

# Wire it: Intent → Pipeline → Processor → Handler
GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,
    pipeline=("inject_db", "handle_get_user"),
)

add_intent(GET_USER, handle_get_user)
register_processor("inject_db", inject_db)
```

**That's IOP.** The Intent declares its pipeline. The pipeline provides dependencies. The handler consumes them.

## Wiring with before()

Use `before()` to attach processors to specific intents:

```python
from evoid.core.extend import before

register_processor("inject_db", inject_db)

# Attach to specific intents
before("get_user", "inject_db")
before("create_user", "inject_db")

# Or use intent name pattern
before("GET:/users/{id}", "inject_db")
```

## Request-Scoped Dependencies

Each pipeline execution gets its own Context — `ctx.deps` is naturally request-scoped:

```python
async def inject_auth(ctx: Context) -> dict:
    token = ctx.intent.metadata.get("authorization")
    ctx.deps["auth"] = await verify_token(token)
    return {"auth_ready": True}

async def inject_db(ctx: Context) -> dict:
    ctx.deps["db"] = create_session()
    return {"db_ready": True}

# Chain multiple injectors in the pipeline
GET_ORDER = Intent(
    name="get_order",
    level=Level.CRITICAL,
    pipeline=("inject_auth", "inject_db", "handle_get_order"),
)
```

!!! warning "Lifecycle"
    Dependencies in `ctx.deps` exist for one pipeline execution. They are not shared between requests.

## Shared State Between Processors

Use `ctx.state` for data flow between processors. Use `ctx.deps` for service instances:

```python
async def fetch_user(intent: Intent, ctx: Context) -> dict:
    """Processor 1: fetch user, store in state."""
    user_id = intent.metadata.get("user_id")
    ctx.state["user"] = await ctx.deps["db"].get_user(user_id)
    return {"fetched": True}

async def check_permissions(intent: Intent, ctx: Context) -> dict:
    """Processor 2: read state, enforce access."""
    user = ctx.state["user"]
    if user.role != "admin":
        raise PermissionError("Admin access required")
    return {"authorized": True}

GET_ADMIN_RESOURCE = Intent(
    name="get_admin_resource",
    level=Level.CRITICAL,
    pipeline=("inject_db", "fetch_user", "check_permissions", "handle_admin"),
)
```

!!! info "state vs deps"
    `ctx.state` = data flow between processors (write in one, read in next).
    `ctx.deps` = service instances injected for the request (DB, auth, cache).

## Singleton Dependencies

For services that hold connections (database pools, HTTP clients), create once at module level:

```python
# services/cache.py
from evoid import register_processor
from evoid.core import Context

# Module-level singleton — one instance for the process
_cache_client = create_redis_client()

async def inject_cache(ctx: Context) -> dict:
    """Inject the singleton cache client."""
    ctx.deps["cache"] = _cache_client
    return {"cache_injected": True}

register_processor("inject_cache", inject_cache)
```

## @route Style

`@route` decorators auto-create Intents. Use `ctx` for injected dependencies:

```python
from evoid.adapters.asgi import get, post
from evoid.web.route import Service

app = Service("api")

@app.on("inject_db")
async def inject_db(ctx: Context) -> dict:
    ctx.deps["db"] = create_session()
    return {"db_injected": True}

@get("/orders/{id}")
async def get_order(id: int, ctx: Context) -> dict:
    db = ctx.deps["db"]
    order = await db.get_order(id)
    return {"id": order.id, "status": order.status}
```

## @controller Style

Group related routes under a prefix:

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("api")

@Controller("/orders")
class OrderController:
    @GET("/{order_id}")
    async def get_order(self, order_id: int, ctx: Context) -> dict:
        db = ctx.deps["db"]
        return {"id": order_id}

    @POST("/")
    async def create_order(self, item_id: int, quantity: int, ctx: Context) -> dict:
        return {"status": "created"}
```

## Summary

| Pattern | Best For | Mechanism |
|---------|----------|-----------|
| Pipeline injection | Per-request services | Processor writes `ctx.deps`, handler reads |
| `ctx.state` | Data between processors | Write in one, read in next |
| Module singleton | Connection pools | One instance per process |
| `before()` | Wiring processors to intents | `before("intent_name", "processor_name")` |
| Pipeline composition | Chaining injectors | `pipeline=("inject_db", "handle")` |

## Plugins and DI

The `evoid-di` plugin takes this further — three levels of dependency injection:

```python
from evoid_di import DIEngine

# Level 1: Simple — name in, instance out
di = DIEngine()
di.register("db", create_db)
db = di.resolve("db")

# Level 2: Scoped — singleton, transient, or per-user
di.register("db", create_db, scope="singleton")  # One connection for all requests
di.register("session", create_session, scope="per_user")  # One session per user

# Level 3: Context-aware — different impl based on Intent level
di = DIEngine(rules_config=rules, implementations=impls)
# CRITICAL intent → PostgreSQL (ACID, audit-friendly)
# STANDARD intent → SQLite (simple, fast)
# EPHEMERAL intent → Redis (temporary, fast)
```

!!! example "IOP: level-aware DI"
    ```python
    # Same database interface, different backends per level
    # The Intent level determines which database you get
    
    PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)
    # → DI injects PostgreSQL (ACID transactions for money)
    
    GET_PROFILE = Intent(name="get_profile", level=Level.STANDARD)
    # → DI injects SQLite (simple user data)
    
    CACHE_CHECK = Intent(name="cache_check", level=Level.EPHEMERAL)
    # → DI injects Redis (temporary, fast)
    
    # Your handler doesn't know which database it got.
    # It just calls ctx.deps["db"].read(...)
    # The DI plugin figured out the rest based on the level.
    ```
