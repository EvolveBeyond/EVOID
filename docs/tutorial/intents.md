# Intents

In the previous step, you created a service with `@get` and `@post` decorators.

**But what happened behind the scenes?**

## The Magic Behind Decorators

When you write:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}
```

EVOID automatically creates an **Intent**:

```
Intent(name="GET:/users/{user_id}", level=STANDARD)
```

This Intent tells the runtime **what** this endpoint does, not **how**.

## What is an Intent?

An Intent is a declaration of purpose. It's pure data:

```python
from evoid import Intent, Level

intent = Intent(
    name="process_payment",      # What this does
    level=Level.CRITICAL,         # How important it is
    metadata={"timeout": 30.0},  # Extra info
    priority=10,                 # Execution priority
)
```

## Intent Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `EPHEMERAL` | Temporary, aggressive cache | Session data, tokens |
| `STANDARD` | Normal processing | Business data |
| `CRITICAL` | Strong consistency, encryption | Financial, auth data |

## Auto-Created Intents

In FastAPI style, intents are created automatically:

```python
@get("/users/{id}")           # Intent: "GET:/users/{id}" (STANDARD)
@post("/payments")            # Intent: "POST:/payments" (STANDARD)
@get("/health", level="ephemeral")  # Intent: "GET:/health" (EPHEMERAL)
```

## What's Next?

Now let's add logic to our Intents with [Processors](processors.md).
