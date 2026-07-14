# Authentication

Secure your API with authentication.

## Using Auth Processor

```python
from evoid import Intent, Level, add_intent_with_pipeline
from evoid.processors import auth_checker

# Register auth processor
from evoid import register_processor
register_processor("auth_checker", auth_checker)

# Add to pipeline
add_intent_with_pipeline(
    Intent(name="process_payment", level=Level.CRITICAL),
    processors=["auth_checker", "validate", "pay"],
    handler=handle_payment,
)
```

## Custom Auth Processor

```python
from evoid.core import Context

async def custom_auth(ctx: Context) -> dict:
    """Check if user is authenticated."""
    token = ctx.intent.metadata.get("headers", {}).get("authorization")

    if not token:
        return {"authenticated": False, "reason": "no_token"}

    # Verify token
    user = verify_token(token)
    if user:
        ctx.state["user"] = user
        return {"authenticated": True}
    else:
        return {"authenticated": False, "reason": "invalid_token"}

register_processor("custom_auth", custom_auth)
```

## Use in Pipeline

```python
add_intent_with_pipeline(
    Intent(name="protected_route", level=Level.STANDARD),
    processors=["custom_auth", "validate", "handler"],
    handler=my_handler,
)
```

## Why Auth as Processor? 🤔

- ✅ **Composable** — Mix auth with other processors
- ✅ **Testable** — Test auth separately
- ✅ **Reusable** — Use same auth across endpoints
- ✅ **Flexible** — Different auth for different endpoints

**Auth is just another processor.** 🔐
