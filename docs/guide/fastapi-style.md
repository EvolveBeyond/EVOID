# @route

Familiar syntax for FastAPI users. Intents are auto-created.

## Basic Usage

```python
from evoid.web.route import Service, get, post, put, delete, run

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created"}

@app.get("/health")
async def health() -> dict:
    return {"status": "healthy"}

# Run
import asyncio
asyncio.run(run(app, port=8000))
```

## How Intent is Created

```
@get("/users/{user_id}")
    ↓
Intent(name="GET:/users/{user_id}", level=STANDARD)
    ↓
register(intent)
    ↓
register_processor(intent.name, handler)
```

## Setting Intent Level

```python
@get("/payments", level="critical")
async def get_payment(payment_id: int) -> dict:
    return {"id": payment_id}
```

## Extending Pipelines

```python
from evoid.web.route import before, after

before("GET:/users/{id}", "log_request")
after("GET:/users/{id}", "log_response")
```
