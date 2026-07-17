---
title: 'Validation'
description: 'Use any validation library with EVOID — Pydantic, msgspec, or your own.'
---

# Validation

EVOID provides the interface. You bring your own library.

## The Principle

Validation is a processor concern. EVOID defines the protocol, you choose the library.

```python
class SchemaEngine(Protocol):
    def validate(self, data: Any, schema: type) -> Any: ...
    def serialize(self, obj: Any) -> dict[str, Any]: ...
    def deserialize(self, data: dict[str, Any], schema: type) -> Any: ...
```

Three methods. That's the entire contract.

## Default: stdlib dataclasses

No dependencies needed:

```python
from evoid.engines.schema import get_validator
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

validator = get_validator()
user = validator.validate({"name": "Alice", "age": 30}, User)
# user is a User dataclass instance
```

## With Pydantic

```python
from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    name: str = Field(min_length=1)
    email: str
    age: int = Field(ge=0, le=150)

validator = get_validator()

# Validate + deserialize
user = validator.validate({"name": "Alice", "email": "a@b.com", "age": 30}, CreateUser)

# Serialize back to dict
data = validator.serialize(user)
```

## With msgspec

```python
import msgspec

class User(msgspec.Struct):
    name: str
    age: int

validator = get_validator()

# Fastest validation in Python
user = validator.validate({"name": "Alice", "age": 30}, User)
data = validator.serialize(user)
```

## Custom Validator

Implement the protocol with your preferred library:

```python
from evoid.engines.schema import set_validator

class MyValidator:
    def validate(self, data, schema):
        # Your validation logic
        ...

    def serialize(self, obj):
        # Your serialization logic
        ...

    def deserialize(self, data, schema):
        # Your deserialization logic
        ...

set_validator(MyValidator())
```

## Auto-Detection Priority

1. **msgspec** — fastest (if installed)
2. **pydantic** — with full validation (if installed)
3. **stdlib dataclasses** — always available (fallback)

## As a Processor

Validation is a processor in the pipeline:

```python
from evoid.engines.schema import get_validator
from evoid import Context

validator = get_validator()

async def validate_body(ctx: Context) -> dict:
    body = ctx.metadata.get("body", {})
    ctx.metadata["body"] = validator.validate(body, CreateUser)
    return {"validated": True}

# Attach to intent
CREATE_USER = Intent(
    name="POST:/users",
    level=Level.STANDARD,
    metadata={
        "processors": ("validate_body",),
    },
)
```

## Native IOP Style

```python
from evoid.native import create_service, on
from evoid import Intent, Level, Context
from evoid.engines.schema import get_validator

app = create_service("api")
validator = get_validator()

async def validate_user(ctx: Context) -> dict:
    body = ctx.metadata.get("body", {})
    ctx.metadata["body"] = validator.validate(body, CreateUser)
    return {"validated": True}

CREATE_USER = Intent(
    name="POST:/users",
    level=Level.STANDARD,
    metadata={
        "method": "POST",
        "path": "/users",
        "processors": ("validate_user",),
    },
)

async def handle_create_user(intent: Intent) -> dict:
    user = intent.metadata["body"]
    return {"status": "created", "name": user.name}

on(app, CREATE_USER, handle_create_user)
```

## Summary

| Library | Install | Speed | Features |
|---------|---------|-------|----------|
| stdlib dataclasses | built-in | baseline | basic |
| pydantic | `pip install pydantic` | good | full validation, serialization |
| msgspec | `pip install msgspec` | fastest | struct validation |

!!! tip "IOP principle"
    EVOID doesn't care which library you use. Just implement the protocol and register it. The pipeline runs the same way regardless.
