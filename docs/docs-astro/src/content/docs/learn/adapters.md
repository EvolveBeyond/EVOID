---
title: Adapters
description: How EVOID connects to the outside world through adapters
---

EVOID is a runtime. It does not care whether your data comes from HTTP, a CLI, a Telegram bot, or a WebSocket. **Adapters** bridge the outside world to EVOID's Intent pipeline.

## What an Adapter Does

An adapter does two things:

1. **Converts external events to Intents** — an HTTP request becomes an Intent, a CLI command becomes an Intent, a Telegram message becomes an Intent.
2. **Converts results back** — the pipeline returns a result, the adapter turns it into an HTTP response, CLI output, or Telegram message.

```
External Event → Adapter → Intent → Pipeline → Result → Adapter → Response
```

EVOID ships with five adapters. Each one provides its own interface because each one handles a different type of event.

## Available Adapters

### ASGI (HTTP)

The most common adapter. Converts HTTP requests to Intents using Starlette.

```python
from evoid.adapters.asgi import get, post, create_app, run

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "user": {"name": name, "email": email}}
```

Route decorators (`get`, `post`, `put`, `delete`) live in the adapter because param extraction is adapter-specific. ASGI reads params from query strings and request bodies.

**Requires:** `pip install starlette uvicorn` or `uv add evoid[asgi]`

### Robyn

High-performance alternative to ASGI. Same concept, different framework.

```python
from evoid.adapters.robyn import create_app, get, post, run_app

app = create_app("my-api")

@get(app, "/users/{user_id}")
async def get_user(intent) -> dict:
    return {"id": 1}

run_app(app, port=8000)
```

Robyn's decorators take `app` as the first argument — that's the adapter-specific difference.

**Requires:** `pip install robyn` or `uv add evoid[robyn]`

### Telegram (aiogram)

Converts Telegram messages and commands to Intents.

```python
from evoid.adapters.telegram import create_bot, on, run_bot
from evoid import Intent

bot = create_bot("YOUR_BOT_TOKEN")

async def start(intent: Intent) -> str:
    return "Welcome!"

async def echo(intent: Intent) -> str:
    text = intent.metadata.get("text", "")
    return f"You said: {text}"

on(bot, "command:/start", start)
on(bot, "message", echo)

import asyncio
asyncio.run(run_bot(bot))
```

No route decorators here — Telegram uses `on(bot, event_type, handler)` because Telegram events are messages and commands, not HTTP routes.

**Requires:** `pip install aiogram` or `uv add evoid[telegram]`

### CLI

Converts command-line arguments to Intents.

```python
from evoid.adapters.cli import intent_from_args, response_from_result

# Convert CLI args to Intent
intent = intent_from_args("create-user", kwargs={"name": "Alice", "email": "a@b.com"})

# Convert result to CLI output
output = response_from_result({"status": "created", "id": 1})
```

No decorators — CLI is a single-shot adapter. You call `intent_from_args` directly.

### MCP (AI Agents)

Exposes Intents as MCP tools for AI agents.

```python
from evoid import export_schemas
from evoid.adapters.mcp import create_mcp_server

schemas = export_schemas()
server = create_mcp_server("my-api")
```

No route decorators — MCP is a discovery protocol, not a request handler.

## How Route Decorators Work

Route decorators (`get`, `post`, `put`, `delete`) are **adapter-specific**, not part of EVOID's core. Each adapter provides its own decorators because each one extracts params differently:

| Adapter | Decorator signature | Param source |
|:--------|:-------------------|:-------------|
| ASGI | `@get("/path")` | Query string, request body |
| Robyn | `@get(app, "/path")` | Robyn request object |
| Telegram | `on(bot, "event", handler)` | Message text, user info |
| CLI | `intent_from_args(cmd)` | Command-line args |

Under the hood, every decorator does the same thing: creates an Intent and registers a processor. The difference is how params get from the request into the Intent's metadata.

## Choosing an Adapter

| Use case | Adapter |
|:---------|:--------|
| Web API | ASGI or Robyn |
| Telegram bot | Telegram |
| Command-line tool | CLI |
| AI agent integration | MCP |
| Custom protocol | Write your own |

## Writing a Custom Adapter

An adapter is any object with two methods:

```python
from typing import Protocol, Any
from evoid import Intent

class Adapter(Protocol):
    def intent_from(self, event: Any) -> Intent: ...
    def response_from(self, result: Any) -> Any: ...
```

Implement these two methods and your adapter works with the entire EVOID ecosystem — pipeline, processors, plugins, everything.

See [Custom Adapters](/EVOID/tutorial/custom-adapters) for a full walkthrough.
