---
title: 'Intent'
description: 'An Intent is a frozen dataclass that declares what you want to achieve. It is pure data — the runtime reads it and decides what to do.'
---

# Intent

An **Intent** is a frozen dataclass that declares what you want to achieve. It is pure data — the runtime reads it and decides what to do.

!!! info "Key concept"
    Intents are immutable. Once created, they cannot be changed. This guarantees thread safety and predictable pipeline behavior.

## Structure

```python
from evoid import Intent, Level

MY_INTENT = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/users/{id}"},
    timeout=10.0,
    priority=0,
)
```

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `name` | `str` | required | Unique identifier |
| `level` | `Level` | `STANDARD` | Protection level |
| `metadata` | `dict` | `{}` | Arbitrary data for processors |
| `timeout` | `float \| None` | `None` | Max seconds before timeout |
| `priority` | `int` | `0` | Execution order (higher first) |

## Intent Levels

The level you choose determines which processors run, how long you have, and what infrastructure backs you. This is IOP's core mechanic — data declares what it needs, the level decides how the system responds.

| Level | Pipeline | Timeout | Use Case |
|-------|----------|---------|----------|
| `ephemeral` | `validate` | 5s | Cache, sessions, temp data |
| `standard` | `validate`, `authorize` | 10s | User profiles, posts, comments |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s | Payments, medical, legal |

!!! warning "Choosing the right level"
    Pick the level that matches your data's criticality. Overusing `critical` adds unnecessary overhead. A cache lookup that takes 30 seconds and writes an audit log is浪费.

### Ephemeral — Fast and disposable

**Pipeline:** `validate` only
**Timeout:** 5 seconds
**Mindset:** "I don't care if this disappears"

```python
# Cache lookup — result is temporary by definition
GET_CACHE = Intent(name="cache_check", level=Level.EPHEMERAL)
# Pipeline: validate → handler (5s)
# What happens: data shape check, then your code. That's it.
# No auth. No audit. Fast path. If the data is wrong, check again later.

# Session check — temporary identity
CHECK_SESSION = Intent(name="check_session", level=Level.EPHEMERAL)
# Pipeline: validate → handler (5s)
# What happens: shape check, then session lookup. No permissions needed.
# Sessions expire. That's the point.

# Game position update — frame-by-frame, disposable
PLAYER_MOVE = Intent(name="player_move", level=Level.EPHEMERAL)
# Pipeline: validate → handler (5s)
# What happens: shape check, then position update. No auth for movement.
# If a position update is wrong, the next frame corrects it.

# Health check — pure liveness probe
HEALTH = Intent(name="health_check", level=Level.EPHEMERAL)
# Pipeline: validate → handler (5s)
# What happens: shape check, then "yes I'm alive." No overhead.
```

**Real-world analogy:** Checking the weather on your phone. You glance, you know, you move on. No paperwork, no ID check, no audit trail. If the data is stale, you'll refresh in 5 minutes.

**When to use:** Cache hits, session lookups, temporary state, health checks, telemetry, game position updates, any data where losing it is inconvenience, not damage.

### Standard — Balanced protection

**Pipeline:** `validate` → `authorize`
**Timeout:** 10 seconds
**Mindset:** "Normal business data — check who's asking"

```python
# User profile — someone's identity, worth protecting
GET_PROFILE = Intent(name="get_profile", level=Level.STANDARD)
# Pipeline: validate → authorize → handler (10s)
# What happens: shape check, then auth plugin checks your role.
# viewer? You can read. editor? You can write. guest? Denied.

# Blog post — public content, but author matters
CREATE_POST = Intent(name="create_post", level=Level.STANDARD)
# Pipeline: validate → authorize → handler (10s)
# What happens: shape check, then "are you logged in?"
# You need at least editor role to create posts.

# Order status — business data, needs auth
CHECK_ORDER = Intent(name="check_order", level=Level.STANDARD)
# Pipeline: validate → authorize → handler (10s)
# What happens: shape check, then "is this your order?"
# Users see their own orders. Admins see all.

# Chat message — needs to know who's talking
SEND_MESSAGE = Intent(name="send_message", level=Level.STANDARD)
# Pipeline: validate → authorize → handler (10s)
# What happens: shape check, then "are you in this chat?"
# No anonymous messages. Identity required.
```

**Real-world analogy:** Showing your ID at a reception desk. They verify who you are (authorize), then let you in. No cameras, no guards, no paperwork — just a quick identity check.

**When to use:** Most business operations. User profiles, posts, comments, settings, general CRUD. The bread and butter of any application.

### Critical — Full protection

**Pipeline:** `validate` → `authorize` → `audit` → `protect`
**Timeout:** 30 seconds
**Mindstep:** "This must never be lost — every step logged"

```python
# Payment — real money, real consequences
PROCESS_PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)
# Pipeline: validate → authorize → audit → protect → handler (30s)
# What happens: shape check, auth, EVERYTHING logged to audit trail,
# rate limit + circuit breaker active, then your payment code.
# If this fails, someone needs to know exactly what happened.

# Medical record — legal requirements
SAVE_MEDICAL = Intent(name="save_medical_record", level=Level.CRITICAL)
# Pipeline: validate → authorize → audit → protect → handler (30s)
# What happens: full protection. Every access logged. Every change recorded.
# Compliance isn't optional. The pipeline enforces it.

# Legal document — must be immutable and auditable
SIGN_CONTRACT = Intent(name="sign_contract", level=Level.CRITICAL)
# Pipeline: validate → authorize → audit → protect → handler (30s)
# What happens: who signed, when, what changed — all recorded.
# In court, the audit trail is your evidence.

# Admin action — elevated privileges, full audit
DELETE_USER = Intent(name="delete_user", level=Level.CRITICAL)
# Pipeline: validate → authorize → audit → protect → handler (30s)
# What happens: who deleted whom, when, why — all logged.
# Admin mistakes are recoverable when you have the audit trail.
```

**Real-world analogy:** Wire transferring a million dollars. You sign papers (authorize), a camera watches you (audit), a guard stands by (protect), and there's a paper trail that lasts forever.

**When to use:** Anything where losing data or making an unauthorized change has real consequences. Payments, medical records, legal documents, authentication, admin operations, data deletion.

## Creating Intents

### Explicit (Native Style)

```python
from evoid import Intent, Level, add_intent

PAYMENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={"currency": "USD"},
)

async def handle_payment(intent: Intent) -> dict:
    return {"status": "processed"}

add_intent(PAYMENT, handle_payment)
```

### Implicit (@route Style)

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service

app = Service("my-api")

@get("/users/{user_id}", level="critical")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}
```

The decorator creates:

- `name`: `GET:/users/{user_id}`
- `level`: `Level.CRITICAL`
- `metadata`: `{"method": "GET", "path": "/users/{user_id}"}`

### Implicit (@controller Style)

```python
from evoid.web.controller import Service, Controller, GET

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{user_id}", level="critical")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}
```

## Intent Metadata

Metadata passes data to processors:

```python
INTENT = Intent(
    name="send_email",
    level=Level.STANDARD,
    metadata={
        "priority": "high",
        "retry": 3,
        "timeout": 30,
        "template": "welcome",
    },
)

async def handle(intent: Intent) -> dict:
    priority = intent.metadata.get("priority", "normal")
    retries = intent.metadata.get("retry", 1)
    return {"sent": True, "priority": priority}
```

## Lifecycle

```
Declaration (you create Intent)
    |
Registration (intent stored in registry)
    |
Resolution (runtime maps intent to PipelineConfig)
    |
Execution (pipeline runs processors in order)
    |
Result (success/failure with value and timing)
```

## Inspecting Registered Intents

```python
from evoid import all_intents

intents = all_intents()
for name, intent in intents.items():
    print(f"{name} [{intent.level.value}]")
```

## Best Practices

- **Use meaningful names** — `get_user` over `handler1`
- **Choose appropriate levels** — Marking everything `critical` defeats the purpose
- **Include useful metadata** — Processors use it for decisions
- **Keep Intents focused** — One intent, one responsibility
- **Set timeouts** — Prevent runaway processors

## Related

- [Pipeline](pipeline.md) — How intents become pipelines
- [Processors](processors.md) — Functions that handle intents
