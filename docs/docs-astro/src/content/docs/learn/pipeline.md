---
title: 'Pipeline'
description: 'A pipeline is a list of processor names executed in order. No class, no state — just data in, result out.'
---

# Pipeline

A pipeline is a list of processor names executed in order. No class, no state — just data in, result out.

!!! tip "Think of it like middleware"
    Each processor in the pipeline is like Express.js middleware or Django's view decorators — they wrap around your handler and add behavior.

## How It Works

When you execute an Intent, EVOID:

1. Resolves the Intent to a `PipelineConfig` (ordered processor names + timeout)
2. Looks up each processor by name in the registry
3. Executes them sequentially, passing a shared `Context`
4. Returns a `Result` with the final value, errors, and timing

```
Intent → Resolver → PipelineConfig → [p1, p2, p3] → Result
```

## Default Pipelines by Level

Each Intent level maps to a default processor chain:

| Level | Processors | Timeout |
|-------|-----------|---------|
| `ephemeral` | `validate` | 5s |
| `standard` | `validate`, `authorize` | 10s |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s |

These defaults are set in the resolver. You override them with the extend system.

## Custom Pipelines

### Add an Intent with a Custom Pipeline

```python
from evoid import Intent, Level
from evoid.core.extend import add_intent_with_pipeline

PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)

async def handle_payment(intent: Intent) -> dict:
    return {"status": "paid"}

add_intent_with_pipeline(
    PAYMENT,
    processors=["validate", "check_fraud", "charge", "notify"],
    handler=handle_payment,
)
```

### Override an Existing Pipeline

```python
from evoid.core.extend import replace_pipeline

replace_pipeline("GET:/users/{id}", ["cache", "fetch_user", "log"])
```

## Pipeline Extensions

!!! danger "DRY violation"
    You have 20 endpoints. Every one needs rate limiting and logging. Copy-pasting the same code into each handler is error-prone and violates DRY.

The solution: inject processors before or after specific routes:

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service, before, after

app = Service("api")

@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}

# Add rate limiting BEFORE all processors
before("GET:/users/{id}", "rate_limit")

# Add logging AFTER all processors
after("GET:/users/{id}", "log_response")
```

Now every `GET:/users/{id}` request runs: `rate_limit` → `validate` → `authorize` → `get_user` → `log_response`.

### Extension Functions

Inject processors without replacing the whole pipeline:

```python
from evoid.core.extend import before, after, before_processor, after_processor

# Add before the first processor
before("process_payment", "rate_limit")

# Add after the last processor
after("process_payment", "send_receipt")

# Add before a specific processor
before_processor("process_payment", "authorize", "check_fraud")

# Add after a specific processor
after_processor("process_payment", "validate", "enrich_data")

# Remove a processor
from evoid.core.extend import remove_processor
remove_processor("process_payment", "audit")
```

## Result

Every pipeline execution returns a `Result`:

```python
from evoid import execute, Intent, Level

async def main():
    intent = Intent(name="get_user", level=Level.STANDARD)
    result = await execute(intent)

    if result.success:
        print(f"Value: {result.value}")
    else:
        print(f"Error: {result.error}")

    print(f"Processors: {result.processors}")
    print(f"Duration: {result.duration:.3f}s")
```

`Result` fields:

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the pipeline completed without error |
| `value` | `Any` | Return value from the last processor |
| `error` | `Exception \| None` | Exception if a processor failed |
| `processors` | `tuple[str, ...]` | Names of processors that ran |
| `duration` | `float` | Total execution time in seconds |

## Context

Each processor receives a `Context` — a mutable databag:

```python
from evoid.core import Context

async def my_processor(ctx: Context) -> dict:
    # Read from state
    user = ctx.state.get("user")

    # Write to state (next processor sees this)
    ctx.state["enriched"] = True

    # Access intent metadata
    method = ctx.intent.metadata.get("method")

    # Access dependencies (engines, etc.)
    db = ctx.deps.get("storage")

    return {"processed": True}
```

`Context` fields:

| Field | Type | Description |
|-------|------|-------------|
| `intent` | `Intent` | The intent being processed |
| `state` | `dict` | Shared state between processors |
| `deps` | `dict` | Injected dependencies (engines, etc.) |
| `metadata` | `dict` | Extra metadata (request params, body, etc.) |
| `errors` | `list[Exception]` | Accumulated errors |
| `id` | `str` | Unique context ID (auto-generated) |

### Forking Contexts

Create a child context for parallel branches:

```python
from evoid.core import fork

child = fork(ctx)
# child has same intent + deps, copied state, parent_id in metadata
```

## Timeout

Set per-Intent or per-pipeline:

```python
from evoid import Intent, Level

# Per-intent timeout
intent = Intent(
    name="slow_operation",
    level=Level.CRITICAL,
    timeout=60.0,  # 60 seconds
)

# Or override via extend
from evoid.core.extend import get_pipeline_config
# Timeout is part of PipelineConfig
```

If a processor exceeds the timeout, the pipeline returns a failed `Result` with `TimeoutError`.

## Error Handling

When a processor raises an exception:

1. Execution stops immediately
2. `Result.success = False`
3. `Result.error` contains the exception
4. `Result.processors` lists what ran before the failure

```python
result = await execute(intent)

if not result.success:
    print(f"Failed after {len(result.processors)} processors")
    print(f"Error: {result.error}")
```

## Inspecting Overrides

```python
from evoid.core.extend import list_overrides, clear_overrides

# See all pipeline overrides
overrides = list_overrides()
# {"GET:/users/{id}": ["cache", "fetch", "log"], ...}

# Clear all overrides
clear_overrides()
```
