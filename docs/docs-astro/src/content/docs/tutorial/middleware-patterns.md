---
title: 'Middleware Patterns'
description: 'Implement cross-cutting concerns using processors.'
---

# Middleware Patterns

Implement cross-cutting concerns using processors.

In IOP, processors are your middleware. No separate system needed.

## How Processors Replace Middleware

Traditional middleware wraps every request. In EVOID, processors run in the pipeline before and after your handler — same result, simpler model.

```python
from evoid.web.route import Service, get, before, after

app = Service("api")

@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}

# These processors run for every matching request
before("GET:/users/{id}", "timing")
after("GET:/users/{id}", "log_response")
```

Pipeline order: `timing` → handler → `log_response`.

## Logging Processor

Record every incoming request with timing:

```python
import time
from evoid.core import Context
from evoid import register_processor

async def log_request(ctx: Context) -> dict:
    ctx.state["start_time"] = time.monotonic()
    method = ctx.intent.metadata.get("method", "?")
    path = ctx.intent.metadata.get("path", "?")
    print(f"[{method} {path}] started")
    return {"logged": True}

register_processor("log_request", log_request)
```

## Timing Processor

Measure handler execution time and attach it to the result:

```python
import time
from evoid.core import Context
from evoid import register_processor

async def timing(ctx: Context) -> dict:
    ctx.state["start_time"] = time.monotonic()
    return {"timing_started": True}

async def report_timing(ctx: Context) -> dict:
    start = ctx.state.get("start_time")
    if start:
        elapsed = time.monotonic() - start
        ctx.state["duration"] = elapsed
        print(f"[{ctx.intent.name}] completed in {elapsed:.3f}s")
    return {"timing_reported": True}

register_processor("timing", timing)
register_processor("report_timing", report_timing)
```

```python
from evoid.web.route import Service, get, before, after

app = Service("api")

@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}

before("GET:/users/{id}", "timing")
after("GET:/users/{id}", "report_timing")
```

## Rate Limiting Processor

Limit requests per intent with a sliding window:

```python
from collections import defaultdict
from time import time
from evoid.core import Context
from evoid import register_processor

_calls: dict[str, list[float]] = defaultdict(list)

async def rate_limit(ctx: Context) -> dict:
    name = ctx.intent.name
    now = time()
    window = 60  # 1 minute
    max_calls = 100

    _calls[name] = [t for t in _calls[name] if now - t < window]

    if len(_calls[name]) >= max_calls:
        raise Exception(f"Rate limit exceeded for {name}")

    _calls[name].append(now)
    return {"rate_limited": False}

register_processor("rate_limit", rate_limit)
```

Apply it to specific routes:

```python
from evoid.web.route import Service, get, post, before

app = Service("api")

before("POST:/orders", "rate_limit")
before("POST:/payments", "rate_limit")
```

## Error Tracking Processor

Collect errors without stopping the pipeline:

```python
from evoid.core import Context
from evoid import register_processor

async def track_errors(ctx: Context) -> dict:
    if ctx.errors:
        for error in ctx.errors:
            print(f"[ERROR] {ctx.intent.name}: {error}")
    return {"errors_tracked": len(ctx.errors)}

register_processor("track_errors", track_errors)
```

## Applying Processors Globally

Use `before()` and `after()` from `evoid.core.extend` to attach processors to any intent:

```python
from evoid.core.extend import before, after

# Apply to one route
before("GET:/users/{id}", "timing")
after("GET:/users/{id}", "report_timing")

# Apply to multiple routes
for route in ["GET:/users/{id}", "POST:/users", "PUT:/users/{id}"]:
    before(route, "rate_limit")
    after(route, "track_errors")
```

!!! tip "Global hooks"
    To apply a processor to every route, add it in your pipeline config in `evoid.toml`:

    ```toml
    [pipeline]
    processors = ["timing", "log_request"]
    ```

## @route Style

```python
from evoid.web.route import Service, get, post, before, after

app = Service("api")

@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created"}

# Apply timing and logging to all routes
for route in ["GET:/users/{id}", "POST:/users"]:
    before(route, "timing")
    after(route, "report_timing")
```

## @controller Style

```python
from evoid.web.controller import Service, Controller, GET, POST, before, after

app = Service("api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}

    @POST("/")
    async def create_user(self, name: str) -> dict:
        return {"status": "created"}

# Apply middleware to all controller routes
before("GET:/users/{user_id}", "timing")
after("GET:/users/{user_id}", "report_timing")
```

## Native IOP Style

```python
from evoid import Intent, Level, add_intent
from evoid.core.extend import add_intent_with_pipeline

GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def handle_get_user(intent: Intent) -> dict:
    return {"id": 1}

add_intent_with_pipeline(
    GET_USER,
    processors=["timing", "log_request", "handle_get_user", "report_timing"],
    handler=handle_get_user,
)
```

## Summary

| Pattern | Processor | Placement |
|---------|-----------|-----------|
| Logging | `log_request` | `before()` |
| Timing | `timing` / `report_timing` | `before()` / `after()` |
| Rate limiting | `rate_limit` | `before()` |
| Error tracking | `track_errors` | `after()` |
| Global hooks | Pipeline config in `evoid.toml` | All routes |
