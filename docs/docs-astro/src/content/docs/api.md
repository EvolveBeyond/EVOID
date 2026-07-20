---
title: 'API Reference'
description: 'Complete reference for the EVOID public API.'
---

# API Reference

Complete reference for the EVOID public API.

## Core Imports

```python
from evoid import (
    # Intent & Pipeline
    Intent, Level, PipelineConfig, Result, Context,
    register, resolve, all_intents, clear_registry,
    resolve_pipeline, execute_pipeline, fork,
    Processor, register_processor, get_processor, all_processors,
    Config, execute, execute_by_name,

    # Message Bus
    Message, subscribe, unsubscribe, publish, get_history, Service,

    # Events (Plugin Hooks)
    Event, EventContext, on_event, off_event, emit, emit_sync, hook_count,

    # Schema Export (AI Agent)
    IntentSchema, export_schemas, export_schema_for,
    export_json_schemas, export_json_schema,

    # Extend
    add_intent, add_intent_with_pipeline,
    before, after, before_processor, after_processor,
    replace_pipeline, remove_processor, get_pipeline_config, list_overrides, clear_overrides,

    # Parallel
    gather, gather_with_priority, parallel, run_in_thread, run_in_thread_async, IntentQueue,

    # Native
    NativeService, create_service, native_on, execute_service,
)
```

---

## Intent

```python
@dataclass(frozen=True)
class Intent:
    name: str
    level: Level = Level.STANDARD
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout: float | None = None
    priority: int = 0
```

Frozen dataclass. Pure data. The runtime reads it, never mutates it.

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Unique identifier for this intent |
| `level` | `Level` | `STANDARD` | Importance level (ephemeral/standard/critical) |
| `metadata` | `dict` | `{}` | Arbitrary data passed to processors |
| `timeout` | `float \| None` | `None` | Max execution time in seconds |
| `priority` | `int` | `0` | Execution priority (higher = first) |

**Examples:**

```python
# Simple intent
GET_USER = Intent(name="get_user", level=Level.STANDARD)

# With metadata
CREATE_ORDER = Intent(
    name="create_order",
    level=Level.CRITICAL,
    metadata={"method": "POST", "path": "/orders"},
    timeout=15.0,
)

# Execute with extra metadata
result = await execute(CREATE_ORDER, amount=99.99, currency="USD")
# Access in processor: ctx.intent.metadata["amount"] → 99.99
```

---

## Level

```python
class Level(str, Enum):
    EPHEMERAL = "ephemeral"
    STANDARD = "standard"
    CRITICAL = "critical"
```

Each level maps to a default pipeline and timeout:

| Level | Default Pipeline | Default Timeout |
|-------|-----------------|-----------------|
| `EPHEMERAL` | `("validate",)` | 5.0s |
| `STANDARD` | `("validate", "authorize")` | 10.0s |
| `CRITICAL` | `("validate", "authorize", "audit", "protect")` | 30.0s |

---

## Context

```python
@dataclass
class Context:
    intent: Intent
    state: dict[str, Any] = field(default_factory=dict)
    deps: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[Exception] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=...)
```

Mutable execution context passed to every processor.

| Field | Type | Description |
|-------|------|-------------|
| `intent` | `Intent` | The intent being processed |
| `state` | `dict` | Shared state between processors |
| `deps` | `dict` | Injected dependencies (engines, etc.) |
| `metadata` | `dict` | Request params, body, headers |
| `errors` | `list[Exception]` | Accumulated non-fatal errors |
| `id` | `str` | UUID, auto-generated |
| `created_at` | `datetime` | UTC creation timestamp |

**Functions:**

```python
fork(ctx: Context) -> Context
```

Create a child context with the same intent and deps, copied state, and `parent_id` in metadata.

**Examples:**

```python
# Read from state
async def processor_a(ctx: Context) -> dict:
    ctx.state["user"] = await db.get_user(42)
    return {"fetched": True}

# Read what processor_a wrote
async def processor_b(ctx: Context) -> dict:
    user = ctx.state["user"]  # ← set by processor_a
    return {"name": user.name}

# Access dependencies
async def with_deps(ctx: Context) -> dict:
    db = ctx.deps.get("storage")
    cache = ctx.deps.get("cache")
    if db:
        await db.write("logs", {...})
    return {"done": True}

# Accumulate non-fatal errors
async def soft_validate(ctx: Context) -> dict:
    try:
        validate(ctx.state["data"])
    except ValidationError as e:
        ctx.errors.append(e)  # Pipeline continues
    return {"validated": True}

# Fork for parallel processing
async def split(ctx: Context) -> dict:
    child = fork(ctx)
    child.state["branch"] = "analytics"
    # child has same intent + deps, new state copy
    return {"forked": True}
```

---

## Result

```python
@dataclass(frozen=True)
class Result:
    success: bool
    value: Any = None
    error: Exception | None = None
    processors: tuple[str, ...] = ()
    duration: float = 0.0
```

Returned by every pipeline execution.

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | `True` if pipeline completed without error |
| `value` | `Any` | Return value from the last processor |
| `error` | `Exception \| None` | The exception if a processor failed |
| `processors` | `tuple[str, ...]` | Names of processors that ran |
| `duration` | `float` | Total execution time in seconds |

**Examples:**

```python
result = await execute(intent)

# Check success
if result.success:
    print(f"Value: {result.value}")
    print(f"Took {result.duration:.3f}s across {len(result.processors)} processors")

# Handle failure
if not result.success:
    print(f"Error: {result.error}")
    print(f"Failed after: {result.processors}")
    # processors shows what ran before the failure

# Inspect timing
for step in result.steps:  # Only available with Config(inspect=True)
    print(f"  {step.name}: {step.duration:.4f}s")
```

---

## PipelineConfig

```python
@dataclass(frozen=True)
class PipelineConfig:
    processors: tuple[str, ...] = ()
    priority: int = 0
    timeout: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

Describes which processors to run, in what order, with what constraints.

---

## Registry Functions

```python
register(intent: Intent) -> None
```

Register an intent definition in the global registry.

```python
resolve(name: str) -> Intent | None
```

Look up an intent by name. Returns `None` if not found.

```python
all_intents() -> dict[str, Intent]
```

Return a copy of all registered intents.

```python
clear_registry() -> None
```

Remove all registered intents.

---

## Processor Functions

```python
Processor = Callable[[Context], Awaitable[Any]]
```

Type alias. A processor is any async function that takes a `Context` and returns a value.

```python
register_processor(name: str, fn: Processor) -> None
```

Register a processor function by name.

```python
get_processor(name: str) -> Processor | None
```

Look up a processor by name.

```python
all_processors() -> dict[str, Processor]
```

Return a copy of all registered processors.

---

## Runtime Functions

```python
async execute(intent: Intent, config: Config | None = None) -> Result
```

Execute an intent through its resolved pipeline. This is the core function.

Resolution order:

1. Check for user overrides (`extend.get_pipeline_config`)
2. Fall back to default resolution (`resolve_pipeline`)

```python
async execute_by_name(name: str, **kwargs) -> Result
```

Execute a registered intent by name. Extra kwargs are merged into the intent's metadata.

```python
@dataclass
class Config:
    name: str = "evoid-service"
    adapter: str = "asgi"
    engines: dict[str, str] = field(default_factory=dict)
```

**Examples:**

```python
from evoid import execute, execute_by_name, Intent, Level
from evoid.core.runtime import Config

# Execute an intent
intent = Intent(name="get_user", level=Level.STANDARD)
result = await execute(intent, user_id=42)
# ctx.intent.metadata["user_id"] → 42

# Execute by name (must be registered first)
result = await execute_by_name("get_user", user_id=42)

# With inspection (dev mode)
config = Config(inspect=True)
result = await execute(intent, config=config)
for step in result.steps:
    print(f"{step.name}: {step.duration:.4f}s")

# With timeout override
config = Config(name="my-service", timeout=30.0)
result = await execute(intent, config=config)
```

---

## Extend Functions

### Add Intents

```python
add_intent(intent: Intent, handler: Callable) -> None
```

Register an intent and its handler as a processor.

```python
add_intent_with_pipeline(
    intent: Intent,
    processors: list[str],
    handler: Callable | None = None,
) -> None
```

Register an intent with a custom processor chain.

**Examples:**

```python
from evoid import Intent, Level
from evoid.core.extend import add_intent, add_intent_with_pipeline

# Simple: register intent + handler
PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)

async def handle_payment(intent: Intent) -> dict:
    return {"status": "paid"}

add_intent(PAYMENT, handle_payment)

# Custom pipeline: specific processor chain
add_intent_with_pipeline(
    PAYMENT,
    processors=["validate", "check_fraud", "charge", "audit"],
    handler=handle_payment,
)
```

### Modify Pipelines

```python
before(intent_name: str, processor_name: str) -> None
```

Insert a processor at the start of the pipeline.

```python
after(intent_name: str, processor_name: str) -> None
```

Append a processor at the end of the pipeline.

```python
before_processor(intent_name: str, target: str, new: str) -> None
```

Insert before a specific processor.

```python
after_processor(intent_name: str, target: str, new: str) -> None
```

Insert after a specific processor.

```python
replace_pipeline(intent_name: str, processors: list[str]) -> None
```

Replace the entire pipeline.

```python
remove_processor(intent_name: str, processor_name: str) -> None
```

Remove a processor from the pipeline.

**Examples:**

```python
from evoid.core.extend import (
    before, after, before_processor, after_processor,
    replace_pipeline, remove_processor,
)

# Add rate limiting before all processors
before("GET:/users/{id}", "rate_limit")

# Add logging after all processors
after("GET:/users/{id}", "log_response")

# Insert auth check before validation
before_processor("POST:/orders", "validate", "check_auth")

# Add audit after authorization
after_processor("POST:/orders", "authorize", "audit_log")

# Replace entire pipeline for health checks
replace_pipeline("GET:/health", ["handle_health"])

# Remove a processor
remove_processor("POST:/orders", "audit_log")
```

### Introspection

```python
get_pipeline_config(intent: Intent) -> PipelineConfig
```

Get the effective pipeline config for an intent (overrides applied).

```python
list_overrides() -> dict[str, list[str]]
```

Return all pipeline overrides as `{intent_name: [processor_names]}`.

```python
clear_overrides() -> None
```

Remove all pipeline overrides.

---

## Message Bus

```python
@dataclass(frozen=True)
class Message:
    intent: Intent
    source: str = ""
    target: str = ""
    reply_to: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

### Functions

```python
subscribe(topic: str, handler: Callable[[Intent], Awaitable[Any]]) -> None
```

Subscribe to a topic. Topics match by intent name, level, or `*` (wildcard).

```python
unsubscribe(topic: str, handler: Callable) -> bool
```

Remove a subscription. Returns `True` if found and removed.

```python
async publish(intent: Intent, source: str = "", target: str = "") -> list[Any]
```

Publish an intent to all matching subscribers. Handlers run concurrently. Returns list of results.

```python
get_history() -> list[Message]
```

Return a copy of all published messages (for debugging).

**Examples:**

```python
from evoid.core.message_bus import publish, subscribe, get_history, clear_history
from evoid import Intent, Level

# Subscribe to events
async def on_order(intent: Intent) -> dict:
    print(f"Order received: {intent.metadata}")
    return {"processed": True}

subscribe("order_placed", on_order)
subscribe("critical", on_order)  # All critical intents
subscribe("*", on_order)  # All intents

# Publish an event
result = await publish(
    Intent(name="order_placed", level=Level.STANDARD, metadata={"item": "BLT"}),
    source="orders",
)

# Debug: see all messages
history = get_history()
for msg in history:
    print(f"{msg.source} → {msg.intent.name}")

# Clear history in tests
clear_history()
```

---

## Parallel Execution

```python
async gather(
    *intents: Intent,
    concurrency: int = 10,
    return_exceptions: bool = False,
) -> list[Result]
```

Execute multiple intents in parallel with a concurrency limit.

```python
async gather_with_priority(
    *intents: Intent,
    concurrency: int = 10,
) -> list[Result]
```

Execute intents sorted by priority (higher first).

```python
async parallel(
    *funcs: Callable[[], Awaitable[Any]],
    concurrency: int = 10,
) -> list[Any]
```

Execute arbitrary async functions in parallel.

```python
run_in_thread(func, *args, **kwargs) -> Any
```

Run a synchronous function in a thread pool (blocking).

```python
async run_in_thread_async(func, *args, **kwargs) -> Any
```

Run a synchronous function in a thread pool (async).

**Examples:**

```python
from evoid import Intent, Level
from evoid.core.parallel import gather, gather_with_priority, run_in_thread_async

# Process 4 orders in parallel
orders = [
    Intent(name="process_order", level=Level.STANDARD, metadata={"location": "downtown"}),
    Intent(name="process_order", level=Level.STANDARD, metadata={"location": "mall"}),
    Intent(name="process_order", level=Level.STANDARD, metadata={"location": "airport"}),
    Intent(name="process_order", level=Level.STANDARD, metadata={"location": "uni"}),
]

results = await gather(orders, concurrency=3)  # Max 3 at a time
for r in results:
    print(f"{'OK' if r.success else 'FAIL'}: {r.value}")

# Priority order: critical first
urgent = Intent(name="vip_order", level=Level.CRITICAL, priority=10)
normal = Intent(name="regular_order", level=Level.STANDARD, priority=5)
results = await gather_with_priority(urgent, normal)

# CPU-bound work in thread pool
import json
def heavy_parse(data):
    return json.loads(data)

result = await run_in_thread_async(heavy_parse, large_json_string)
```

### IntentQueue

```python
class IntentQueue:
    def __init__(self, max_concurrent: int = 10) -> None: ...
    def enqueue(self, intent: Intent, priority: int = 0) -> None: ...
    def dequeue(self) -> Intent | None: ...
    async def process(self) -> list[Result]: ...
    @property
    def size(self) -> int: ...
    @property
    def is_empty(self) -> bool: ...
```

Priority queue for ordered intent execution.

---

## Service (Core)

```python
@dataclass
class Service:
    name: str
    handlers: dict[str, Handler] = field(default_factory=dict)
    running: bool = False
```

```python
start(service: Service) -> None
```

Start a service. Registers all handlers with the message bus.

```python
stop(service: Service) -> None
```

Stop a service.

```python
on(service: Service, intent_name: str, handler: Handler) -> None
```

Register a handler for an intent. If the service is running, registers immediately with the message bus.

```python
async call(service: Service, intent: Intent) -> Any
```

Call another service. Returns the first non-exception result.

```python
async emit(service: Service, intent: Intent) -> list[Any]
```

Fire-and-forget. Publishes to all subscribers without waiting.

---

## @route Style

```python
from evoid.adapters.asgi import get, post, put, delete
from evoid.web.route import Service

app = Service(name: str) -> App
get(path: str, level: str = "standard") -> Callable
post(path: str, level: str = "standard") -> Callable
put(path: str, level: str = "standard") -> Callable
delete(path: str, level: str = "standard") -> Callable
```

**Extend functions:**

```python
before(route: str, processor: str) -> None
after(route: str, processor: str) -> None
before_handler(route: str, target: str, processor: str) -> None
after_handler(route: str, target: str, processor: str) -> None
replace_pipeline(route: str, processors: list[str]) -> None
```

**Run:**

```python
async run(app: App, host: str = "0.0.0.0", port: int = 8000) -> None
```

---

## @controller Style

```python
from evoid.web.controller import Service, Controller, GET, POST, PUT, DELETE

app = Service(name: str) -> App
Controller(prefix: str = "", level: str = "standard") -> Callable
GET(path: str = "", level: str = "standard") -> Callable
POST(path: str = "", level: str = "standard") -> Callable
PUT(path: str = "", level: str = "standard") -> Callable
DELETE(path: str = "", level: str = "standard") -> Callable
```

Same extend functions and `run()` as @route.

---

## Native Style

```python
from evoid.native import create_service, on, run

create_service(name: str) -> Service
on(service: Service, intent: Intent, handler: Handler) -> None
async execute_service(service: Service, intent_name: str, **kwargs) -> Any
async run(service: Service, host: str = "0.0.0.0", port: int = 8000) -> None
```

---

## CLI

```bash
evo init <name>              # Create new project
evo service new <name>       # Add service to project
evo service list             # List services
evo service run <name>       # Run a service
evo sync                     # Sync dependencies from evoid.toml
evo run                      # Run all services
evo serve [host] [port]      # Quick serve (single service)
evo list-intents             # List registered intents
evo list-processors          # List registered processors
evo exec <intent>            # Execute intent by name
evo version                  # Show version
```
