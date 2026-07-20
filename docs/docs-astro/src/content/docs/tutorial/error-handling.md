---
title: 'Error Handling'
description: 'Structured errors, Result objects, and proper HTTP responses.'
---

# Error Handling

Structured errors, Result objects, and proper HTTP responses.

## Raising Exceptions

Any exception stops the pipeline and returns an error:

```python
@get("/menu/{item_id}")
async def get_item(item_id: int) -> dict:
    item = next((m for m in MENU if m["id"] == item_id), None)
    if not item:
        raise ValueError("Item not found")
    return item
```

## What Happens Under the Hood

When you raise an exception in a handler:

```
Request arrives → Intent resolved → Pipeline starts
  ↓
validate → authorize → get_item (raises ValueError)
  ↓
Pipeline stops → Result(success=False, error=ValueError("Item not found"))
  ↓
Adapter converts Result.error to HTTP 500 + {"detail": "Item not found"}
```

The pipeline doesn't catch exceptions — it captures them in `Result.error` and stops. The adapter decides how to present the error to the client.

## Returning Error Dicts

For structured errors, return a dict:

```python
@get("/menu/{item_id}")
async def get_item(item_id: int) -> dict:
    item = next((m for m in MENU if m["id"] == item_id), None)
    if not item:
        return {"error": "Item not found", "status": "not_found"}
    return item
```

## The Result Object

Every pipeline execution returns a Result:

```python
from evoid import execute, Intent, Level

result = await execute(intent)

if result.success:
    print(f"Value: {result.value}")
else:
    print(f"Error: {result.error}")
    print(f"Ran {len(result.processors)} processors before failure")
    print(f"Duration: {result.duration:.3f}s")
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Pipeline completed without exception |
| `value` | `Any` | Return value from last processor |
| `error` | `Exception \| None` | Exception if pipeline failed |
| `processors` | `tuple[str, ...]` | Processors that ran |
| `duration` | `float` | Total execution time |

## Collecting Non-Critical Errors

Use `ctx.errors` to collect warnings without stopping:

```python
async def validate_optional(intent: Intent, ctx: Context) -> dict:
    try:
        validate(ctx.metadata.get("body"))
    except ValidationError as e:
        ctx.errors.append(e)
        # Pipeline continues

    return {"validated": True, "warnings": len(ctx.errors)}
```

## Custom Error Responses

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service

app = Service("sandy-api")

class AppError:
    def __init__(self, message: str, status: int = 400):
        self.message = message
        self.status = status

@get("/orders/{order_id}")
async def get_order(order_id: int) -> dict:
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if not order:
        raise AppError("Order not found", status=404)
    return order
```

## Error Handling Summary

| Scenario | Approach |
|----------|----------|
| Fatal error | `raise Exception("msg")` — pipeline stops |
| Structured error | Return `{"error": "msg"}` |
| Non-critical warning | `ctx.errors.append(e)` — pipeline continues |
| Check result | `result.success`, `result.error` |

## Next: Dependency Injection

Let's manage dependencies properly — [Dependency Injection](dependency-injection.md).
