# Processors

Processors are independent functions that do work in a pipeline.

## What is a Processor? 🧩

A processor is a **pure function** that:

1. Receives a `Context`
2. Does some work
3. Returns a result

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

## Register a Processor

```python
from evoid import register_processor

register_processor("my_processor", my_processor)
```

## Use in Pipeline

```python
from evoid import add_intent_with_pipeline, Intent, Level

add_intent_with_pipeline(
    Intent(name="my_intent", level=Level.STANDARD),
    processors=["my_processor", "validate", "authorize"],
)
```

## Built-in Processors 📦

| Processor | What it does |
|-----------|--------------|
| `intent_extractor` | Extracts intent info |
| `schema_validator` | Validates data |
| `auth_checker` | Checks authorization |
| `rate_limiter` | Limits request rate |
| `circuit_breaker` | Prevents cascading failures |
| `logger_processor` | Logs execution |

## Why Processors? 🤔

Processors are:
- ✅ **Independent** — No dependencies on each other
- ✅ **Composable** — Mix and match as needed
- ✅ **Testable** — Test each processor separately
- ✅ **Reusable** — Use the same processor in multiple pipelines

**Processors are LEGO blocks for your pipeline.** 🧩
