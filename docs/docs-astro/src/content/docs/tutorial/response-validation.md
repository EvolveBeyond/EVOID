---
title: 'Response Validation Patterns'
description: 'Validate handler responses using Pydantic and processors.'
---

# Response Validation Patterns

Validate handler responses using Pydantic and processors.

Response validation is a processor pattern, not a separate feature.

## Define a Response Schema

Start with a Pydantic BaseModel that describes your response:

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
```

## Create a Validation Processor

Write a processor that validates the handler's return value against the schema:

```python
from evoid.core import Context
from evoid import register_processor

async def validate_response(ctx: Context) -> dict:
    """Validate the handler response against its schema."""
    schema = ctx.intent.metadata.get("response_schema")
    if not schema:
        return {"validated": True}

    response = ctx.state.get("response")
    if response is None:
        return {"validated": True}

    schema.model_validate(response)
    return {"validated": True}

register_processor("validate_response", validate_response)
```

## Attach to Intents

Use pipeline config to attach validation to specific routes:

```python
from evoid.web.route import Service, get, after
from models import UserResponse

app = Service("api")

@get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice", "email": "alice@example.com"}

after("GET:/users/{user_id}", "validate_response")
```

## Auto-Detect from Return Type Hints

Read the handler's return type hint and validate against it automatically:

```python
import inspect
from evoid.core import Context
from evoid import register_processor
from pydantic import BaseModel

async def auto_validate(ctx: Context) -> dict:
    """Read return type hint and validate response."""
    handler = ctx.intent.metadata.get("handler")
    if not handler:
        return {"auto_validated": False}

    hint = inspect.get_annotations(handler).get("return")
    if hint and isinstance(hint, type) and issubclass(hint, BaseModel):
        response = ctx.state.get("response")
        if response:
            hint.model_validate(response)

    return {"auto_validated": True}

register_processor("auto_validate", auto_validate)
```

!!! tip "Type hint pattern"
    If your handler returns `-> UserResponse`, the processor validates against `UserResponse` automatically. No config needed per route.

## Error Responses with Consistent Format

Return validation errors in a standard format:

```python
from pydantic import BaseModel, ValidationError

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None

async def validate_or_error(ctx: Context) -> dict:
    schema = ctx.intent.metadata.get("response_schema")
    if not schema:
        return {"validated": True}

    response = ctx.state.get("response")
    try:
        schema.model_validate(response)
        return {"validated": True}
    except ValidationError as e:
        ctx.errors.append(e)
        return {
            "validated": False,
            "response": ErrorResponse(
                error="Validation failed",
                detail=str(e),
            ).model_dump(),
        }

register_processor("validate_or_error", validate_or_error)
```

## @route Style

```python
from evoid.web.route import Service, get, after
from models import UserResponse

app = Service("api")

@get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice", "email": "alice@example.com"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"id": 1, "name": name, "email": email}

after("GET:/users/{user_id}", "validate_response")
after("POST:/users", "validate_response")
```

## @controller Style

```python
from evoid.web.controller import Service, Controller, GET, POST, after
from models import UserResponse

app = Service("api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Alice", "email": "alice@example.com"}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        return {"id": 1, "name": name, "email": email}

after("GET:/users/{user_id}", "validate_response")
after("POST:/users", "validate_response")
```

## Native IOP Style

```python
from evoid import Intent, Level, add_intent
from evoid.core.extend import add_intent_with_pipeline
from models import UserResponse

GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def handle_get_user(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}

add_intent_with_pipeline(
    GET_USER,
    processors=["validate_response", "handle_get_user"],
    handler=handle_get_user,
)
```

## Summary

| Pattern | Mechanism | When to Use |
|---------|-----------|-------------|
| Schema validation | Pydantic BaseModel + processor | Strict API contracts |
| Auto-detect hints | Read `->` return type | Convention over config |
| Error format | Standardize validation errors | Consistent client experience |
| Pipeline attach | `after()` or `evoid.toml` | Per-route or global |
