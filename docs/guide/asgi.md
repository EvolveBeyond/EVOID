# ASGI Adapter

HTTP adapter using Starlette/Uvicorn.

## Basic Usage

```python
from evoid.adapters.asgi import create_app, run

app = create_app(name="my-api")

# Run
run(app, host="0.0.0.0", port=8000)
```

## With Handlers

```python
from evoid.adapters.asgi import create_app, run
from evoid.core import Intent, Level

async def handle_payment(intent: Intent) -> dict:
    return {"status": "success"}

app = create_app(
    name="my-api",
    handlers={
        "POST:/api/payment": handle_payment,
    },
)

run(app, port=8000)
```

## CLI

```bash
evo serve 0.0.0.0 8000
```
