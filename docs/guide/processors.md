# Processors

**Processors** are independent functions that do work in a pipeline.

## Creating a Processor

```python
from evoid.core import Context

async def my_processor(ctx: Context) -> dict:
    # Access intent
    intent_name = ctx.intent.name
    level = ctx.intent.level

    # Access state
    data = ctx.state.get("data")

    # Set state
    ctx.state["result"] = "done"

    return {"processed": True}
```

## Built-in Processors

| Processor | Description |
|-----------|-------------|
| `intent_extractor` | Extracts intent info from context |
| `schema_validator` | Validates data against schema |
| `auth_checker` | Checks authorization |
| `rate_limiter` | Limits request rate |
| `circuit_breaker` | Prevents cascading failures |
| `logger_processor` | Logs pipeline execution |

## Registering Processors

```python
from evoid import register_processor

register_processor("my_processor", my_processor)
```

## Using Processors

```python
from evoid import add_intent_with_pipeline

add_intent_with_pipeline(
    Intent(name="my_intent", level=Level.STANDARD),
    processors=["my_processor", "validate", "authorize"],
)
```
