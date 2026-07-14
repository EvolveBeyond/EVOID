# Examples

## Minimal Example

```python
from evoid.web.route import Service, get, run

app = Service("hello")

@get("/hello")
async def hello() -> dict:
    return {"message": "Hello, EVOID!"}

import asyncio
asyncio.run(run(app, port=8000))
```

## Web API

```python
from evoid.web.route import Service, get, post, run
from evoid.engines.logger import loguru as log

app = Service("api")

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    log.info(f"Getting user {user_id}")
    return {"id": user_id, "name": f"User {user_id}"}

@app.post("/users")
async def create_user(name: str, email: str) -> dict:
    log.info(f"Creating user: {name}")
    return {"status": "created", "user": {"name": name, "email": email}}

import asyncio
asyncio.run(run(app, port=8000))
```

## Inter-Service Communication

```python
from evoid.core import Intent, Level, Service
from evoid.core.service import start, call

payment_service = Service(name="payment")

async def handle_payment(intent: Intent) -> dict:
    return {"status": "success", "amount": intent.metadata.get("amount", 0)}

start(payment_service)

# Call another service
result = await call(
    payment_service,
    Intent(name="process_payment", level=Level.CRITICAL, metadata={"amount": 99.99}),
)
print(result)  # {"status": "success", "amount": 99.99}
```

## Parallel Execution

```python
from evoid import gather, Intent, Level

intent1 = Intent(name="fetch_users", level=Level.STANDARD)
intent2 = Intent(name="fetch_orders", level=Level.STANDARD)
intent3 = Intent(name="fetch_products", level=Level.STANDARD)

# Execute in parallel
results = await gather(intent1, intent2, intent3)
```

## Custom Pipeline

```python
from evoid import Intent, Level, add_intent_with_pipeline

MY_INTENT = Intent(name="complex_op", level=Level.CRITICAL)

async def my_handler(intent: Intent) -> dict:
    return {"status": "done"}

add_intent_with_pipeline(
    MY_INTENT,
    processors=["validate", "transform", "save", "notify"],
    handler=my_handler,
)
```
