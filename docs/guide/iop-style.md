# IOP Native Style

Full control over Intents and pipelines.

## Basic Usage

```python
from evoid import Intent, Level, Context, add_intent, execute
from evoid.web.iop_style import create_service, on, run

# Create service
app = create_service("my-api")

# Define Intents
GET_USER = Intent(name="get_user", level=Level.STANDARD)
CREATE_USER = Intent(name="create_user", level=Level.STANDARD)

# Define handlers
async def get_user(intent: Intent) -> dict:
    user_id = intent.metadata.get("user_id", 0)
    return {"id": user_id, "name": f"User {user_id}"}

async def create_user(intent: Intent) -> dict:
    data = intent.metadata.get("body", {})
    return {"status": "created", "user": data}

# Register
on(app, GET_USER, get_user)
on(app, CREATE_USER, create_user)

# Run
import asyncio
asyncio.run(run(app, port=8000))
```

## Custom Pipelines

```python
from evoid import add_intent_with_pipeline

add_intent_with_pipeline(
    Intent(name="payment", level=Level.CRITICAL),
    processors=["validate", "check_fraud", "pay", "notify"],
    handler=my_handler,
)
```

## Parallel Execution

```python
from evoid import gather, gather_with_priority

# Parallel
results = await gather(intent1, intent2, intent3)

# With priority
results = await gather_with_priority(intent1, intent2, intent3)
```
