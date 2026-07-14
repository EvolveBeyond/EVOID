# IOP Native Style

Full control over Intents and pipelines.

## Basic Usage

```python
from evoid import Intent, Level, Context, add_intent
from evoid.web.iop_style import create_service, on, run

# Create service
app = create_service("my-api")

# Define Intent
MY_INTENT = Intent(name="my_intent", level=Level.STANDARD)

# Define handler
async def handler(intent: Intent) -> dict:
    return {"status": "ok"}

# Register
on(app, MY_INTENT, handler)

# Run
import asyncio
asyncio.run(run(app, port=8000))
```

## Custom Pipeline

```python
from evoid import add_intent_with_pipeline

add_intent_with_pipeline(
    Intent(name="payment", level=Level.CRITICAL),
    processors=["validate", "check_fraud", "pay", "notify"],
    handler=my_handler,
)
```

## When to Use IOP Style? 🤔

| Scenario | Recommended Style |
|----------|-------------------|
| Quick prototype | FastAPI style ✅ |
| Small project (< 10 endpoints) | FastAPI style ✅ |
| Need full control | IOP style ✅ |
| Complex pipelines | IOP style ✅ |
| Custom processors | IOP style ✅ |

**IOP style gives you maximum control.** 🎯
