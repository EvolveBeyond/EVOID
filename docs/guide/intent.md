# Intent

An **Intent** is a declaration of purpose. It's pure data — no behavior.

## Creating Intents

### Explicit (IOP Native)

```python
from evoid import Intent, Level

MY_INTENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={"timeout": 30.0},
    priority=10,
)
```

### Implicit (@route/@controller)

Decorators auto-create Intents:

```python
@get("/users/{id}")
# Auto-creates: Intent(name="GET:/users/{id}", level=STANDARD)

@post("/payments")
# Auto-creates: Intent(name="POST:/payments", level=STANDARD)
```

## Intent Levels

```python
from evoid import Level

Level.EPHEMERAL  # Temporary data, aggressive cache
Level.STANDARD   # Normal business data
Level.CRITICAL   # Vital data, strong consistency
```

## Registering Intents

```python
from evoid import add_intent

MY_INTENT = Intent(name="my_intent", level=Level.STANDARD)

async def handler(intent: Intent) -> dict:
    return {"status": "ok"}

add_intent(MY_INTENT, handler)
```

## Custom Pipelines

```python
from evoid import add_intent_with_pipeline

add_intent_with_pipeline(
    Intent(name="complex_op", level=Level.CRITICAL),
    processors=["validate", "transform", "save", "notify"],
    handler=my_handler,
)
```
