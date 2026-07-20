---
title: 'Examples'
description: 'Working examples that demonstrate EVOID features. All examples are in the `examples/` directory.'
---

# Examples

Working examples that demonstrate EVOID features. All examples are in the `examples/` directory.

## Minimal API

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service

app = Service("minimal")

@get("/")
async def home() -> dict:
    return {"message": "Hello from EVOID!"}
```

```bash
evo service run minimal
curl http://localhost:8000/
# {"message": "Hello from EVOID!"}
```

## CRUD Service

```python
from evoid.adapters.asgi import get, post, put, delete
from evoid.web.route import Service

app = Service("users")
users: list[dict] = []

@get("/users")
async def list_users() -> dict:
    return {"users": users}

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    for u in users:
        if u["id"] == user_id:
            return u
    return {"error": "not found"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    user = {"id": len(users) + 1, "name": name, "email": email}
    users.append(user)
    return user

@delete("/users/{user_id}")
async def delete_user(user_id: int) -> dict:
    global users
    users = [u for u in users if u["id"] != user_id]
    return {"status": "deleted"}
```

## Intent Levels

Different protection levels for different data.

```python
from evoid.adapters.asgi import get, post
from evoid.web.route import Service

app = Service("levels")

@get("/cache-me", level="ephemeral")
async def cache_me() -> dict:
    return {"cached": True}

@get("/users/{id}", level="standard")
async def get_user(id: int) -> dict:
    return {"id": id}

@post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid", "amount": amount}
```

## Pipeline Extensions

Cross-cutting concerns without touching handlers.

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service, before, after

app = Service("extended")

@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}

before("GET:/users/{id}", "rate_limit")
after("GET:/users/{id}", "log_response")
```

## Parallel Execution

Run multiple intents concurrently.

```python
from evoid import Intent, Level, gather, add_intent
from evoid.adapters.asgi import get
from evoid.web.route import Service

app = Service("parallel")

USER_API = Intent(name="fetch_users", level=Level.STANDARD)
ORDER_API = Intent(name="fetch_orders", level=Level.STANDARD)

async def fetch_users(intent: Intent) -> list:
    return [{"id": 1}, {"id": 2}]

async def fetch_orders(intent: Intent) -> list:
    return [{"order_id": 101}, {"order_id": 102}]

add_intent(USER_API, fetch_users)
add_intent(ORDER_API, fetch_orders)

@get("/dashboard")
async def dashboard() -> dict:
    results = await gather(USER_API, ORDER_API)
    return {
        "users": results[0].value,
        "orders": results[1].value,
    }
```

## Inter-Service Communication

Services talking through the message bus.

```python
from evoid import Intent, Level, subscribe, publish
from evoid.native import create_service, on, run

payment_service = create_service("payments")

PAYMENT_INTENT = Intent(name="process_payment", level=Level.CRITICAL)

async def handle_payment(intent: Intent) -> dict:
    amount = intent.metadata.get("amount", 0)
    return {"status": "paid", "amount": amount}

on(payment_service, PAYMENT_INTENT, handle_payment)

async def notify_on_payment(intent: Intent) -> None:
    print(f"Payment of {intent.metadata.get('amount')} received!")

subscribe("process_payment", notify_on_payment)

await run(payment_service, port=8001)
```

## Controller Style

Class-based grouping for larger APIs.

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("shop")

@Controller("/products")
class ProductController:
    @GET("/")
    async def list_products(self) -> dict:
        return {"products": []}

    @GET("/{id}")
    async def get_product(self, id: int) -> dict:
        return {"id": id, "name": "Widget"}

    @POST("/")
    async def create_product(self, name: str, price: float) -> dict:
        return {"status": "created", "name": name}

@Controller("/orders", level="critical")
class OrderController:
    @POST("/")
    async def create_order(self, product_id: int, quantity: int) -> dict:
        return {"status": "ordered"}
```

## Native IOP

Full control with explicit intent management.

```python
from evoid import Intent, Level, add_intent, execute_by_name

SEARCH = Intent(
    name="search",
    level=Level.STANDARD,
    metadata={"timeout": 30},
)

async def handle_search(intent: Intent) -> dict:
    query = intent.metadata.get("query", "")
    return {"results": [f"Result for '{query}'"]}

add_intent(SEARCH, handle_search)

result = await execute_by_name("search", query="hello")
print(result.value)
# {"results": ["Result for 'hello'"]}
```

## Custom Processor

Write a processor and inject it into any pipeline.

```python
from evoid import Intent, Level, add_intent
from evoid.core import Context, register_processor
from evoid.core.extend import before

async def timing_processor(ctx: Context) -> dict:
    import time
    ctx.state["start_time"] = time.monotonic()
    return {"timing_started": True}

register_processor("timing", timing_processor)

PAYMENT = Intent(name="pay", level=Level.CRITICAL)

async def handle_pay(intent: Intent) -> dict:
    return {"paid": True}

add_intent(PAYMENT, handle_pay)
before("pay", "timing")
```

## Message Bus Pub/Sub

Decoupled communication between components.

```python
from evoid import Intent, Level, subscribe, publish

async def on_order_created(intent: Intent) -> None:
    print(f"Order {intent.metadata.get('order_id')} created")

async def on_order_shipped(intent: Intent) -> None:
    print(f"Order {intent.metadata.get('order_id')} shipped")

subscribe("order_created", on_order_created)
subscribe("order_shipped", on_order_shipped)

order = Intent(
    name="order_created",
    level=Level.STANDARD,
    metadata={"order_id": 42, "total": 99.99},
)
await publish(order)
```

## Error Handling

Graceful error handling in pipelines.

```python
from evoid import Intent, Level, execute

async def main():
    intent = Intent(name="get_user", level=Level.STANDARD)
    result = await execute(intent)

    if result.success:
        print(f"Value: {result.value}")
    else:
        print(f"Failed after {len(result.processors)} processors")
        print(f"Error: {result.error}")
        print(f"Duration: {result.duration:.3f}s")
```

## Configuration

Swap infrastructure by changing config.

```toml
# evoid.toml
[engines]
schema = "native"
storage = "sqlite"
cache = "memory"
serializer = "json"
logger = "loguru"
```

Switch to PostgreSQL:

```toml
[engines]
storage = "postgres"
```

Then run `evo sync` to install the new dependency.
