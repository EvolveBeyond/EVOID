# @controller

Class-based syntax for NestJS/TypeScript users. Intents are auto-created.

## Basic Usage

```python
from evoid.web.controller import Service, Controller, GET, POST, run

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": f"User {user_id}"}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created"}

# Run
import asyncio
asyncio.run(run(app, port=8000))
```

## How Intent is Created

```
@Controller("/users")
    ↓
@GET("/{user_id}")
    ↓
Intent(name="GET:/users/{user_id}", level=STANDARD)
    ↓
register(intent)
    ↓
register_processor(intent.name, handler)
```

## Setting Intent Level

```python
@Controller("/payments", level="critical")
class PaymentController:
    @POST("/")
    async def create_payment(self, amount: float) -> dict:
        return {"status": "created"}
```

## Extending Pipelines

```python
from evoid.web.controller import before, after

before("GET:/users/{id}", "log_request")
after("GET:/users/{id}", "log_response")
```
