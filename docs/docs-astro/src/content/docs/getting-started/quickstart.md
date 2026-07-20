---
title: 'Quick Start'
description: 'Build a working EVOID API in 5 minutes.'
---

# Quick Start

Build a working EVOID API in 5 minutes.

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Step 1: Install & Create

```bash
uv add evoid
evo init my-api
cd my-api
```

This creates:

```
my-api/
  evoid.toml
  shared/
  services/
```

## Step 2: Add a Service

```bash
evo service new api
```

This creates `services/api/main.py`.

## Step 3: Write Your First Endpoint

Edit `services/api/main.py`:

```python
from evoid.adapters.asgi import get, post
from evoid.web.route import Service

app = Service("my-api")

@get("/")
async def home() -> dict:
    return {"message": "Hello from EVOID!"}

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "name": name}
```

## Step 4: Run the Server

```bash
evo service run api
```

You should see:

```
Starting my-api on http://0.0.0.0:8000
```

## Step 5: Test It

```bash
# Home
curl http://localhost:8000/
# {"message": "Hello from EVOID!"}

# Get user
curl http://localhost:8000/users/123
# {"id": 123, "name": "User 123"}

# Create user
curl -X POST http://localhost:8000/users?name=Ali&email=ali@example.com
# {"status": "created", "name": "Ali"}
```

!!! info "What just happened?"
    Behind the scenes, EVOID:

    1. **Created Intents** — Each decorator (`@get`, `@post`) created an Intent automatically. `@get("/users/{user_id}")` became `Intent(name="GET:/users/{user_id}", level=Level.STANDARD)`
    2. **Registered Processors** — Your functions were wrapped as processors and registered by intent name
    3. **Set Up ASGI** — An ASGI server was started to handle HTTP requests
    4. **Configured Routing** — URLs were mapped to Intents. When a request arrives, EVOID resolves the intent, builds a pipeline, and executes it

    Three decorators handled all of that. That's IOP — you declare what you want, EVOID handles how.

    ```python
    # What @get("/users/{user_id}") actually creates:
    GET_USER = Intent(
        name="GET:/users/{user_id}",
        level=Level.STANDARD,
        metadata={"method": "GET", "path": "/users/{user_id}"},
    )

    # Your handler is wrapped as a processor:
    async def processor(ctx: Context) -> dict:
        params = ctx.metadata.get("params", {})
        return await get_user(**params)  # Your original function
    ```

!!! tip "Protection levels"
    Each level maps to a different pipeline — `ephemeral` gets fast validation only, `critical` gets full audit and protection.

## Adding Protection Levels

Change the protection level per route:

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

Each level maps to a different pipeline — `ephemeral` gets fast validation only, `critical` gets full audit and protection.
