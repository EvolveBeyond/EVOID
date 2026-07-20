---
title: "@route Style"
description: "Function-based syntax. Familiar if you have used FastAPI or Flask."
---

# @route Style

Function-based syntax. Familiar if you've used FastAPI or Flask. Intents are created automatically from decorators.

## Basic Usage

```python
from evoid.adapters.asgi import get, post, put, delete
from evoid.web.route import Service

app = Service("my-api")

@get("/users")
async def list_users() -> dict:
    return {"users": []}

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "name": name}

@put("/users/{user_id}")
async def update_user(user_id: int, name: str) -> dict:
    return {"id": user_id, "name": name}

@delete("/users/{user_id}")
async def delete_user(user_id: int) -> dict:
    return {"status": "deleted"}
```

## What Happens Under the Hood

Each decorator:

1. Creates an `Intent` with name `METHOD:/path` (e.g., `GET:/users/{user_id}`)
2. Registers the intent
3. Wraps your function as a processor
4. Registers the processor

When a request arrives, EVOID resolves the intent, builds a pipeline, and executes it.

## Intent Levels

Set the importance level per route:

```python
@get("/public/data", level="ephemeral")
async def public_data() -> dict:
    return {"data": "cache me"}

@get("/users/{id}", level="standard")
async def get_user(id: int) -> dict:
    return {"id": id}

@post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid"}
```

## Pipeline Extensions

Add processors before or after specific routes:

```python
from evoid.web.route import before, after, before_handler, after_handler, replace_pipeline

# Add before all processors for this route
before("GET:/users/{id}", "rate_limit")

# Add after all processors
after("GET:/users/{id}", "log_response")

# Add before a specific processor
before_handler("GET:/users/{id}", "authorize", "check_permission")

# Add after a specific processor
after_handler("GET:/users/{id}", "validate", "enrich_data")

# Replace entire pipeline
replace_pipeline("GET:/users/{id}", ["cache", "fetch_user", "serialize"])
```

## Running

```python
from evoid.web.route import run

await run(app, host="0.0.0.0", port=8000)
```

Or via CLI:

```bash
evo service run api
```

## When to Use

- Small to medium APIs
- Teams familiar with FastAPI/Flask
- Quick prototyping
- Services with straightforward routing
