<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/version-0.4.1-orange?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/license-Apache%202.0-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/core%20deps-zero-brightgreen?style=for-the-badge" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/status-Beta-purple?style=for-the-badge" alt="Status">
</p>

<h1 align="center">EVOID</h1>

<p align="center">
  <strong>Reference Runtime for Intent-Oriented Programming</strong>
</p>

<p align="center">
  <em>Data declares what, runtime decides how.</em>
</p>

<p align="center">
  <a href="#what-is-iop">What is IOP?</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#adapters">Adapters</a> •
  <a href="#features">Features</a> •
  <a href="https://evolvebeyond.github.io/EVOID/">Docs</a> •
  <a href="https://pypi.org/project/evoid/">PyPI</a>
</p>

---

## What is IOP?

**Intent-Oriented Programming** — your data declares what it needs, the runtime handles how.

```python
from evoid.native import create_service, on
from evoid import Intent, Level

app = create_service("my-api")

GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def get_user(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

on(app, GET_USER, get_user)
```

Three intent levels control infrastructure automatically:

| Level | Pipeline | Use Case |
|:------|:---------|:---------|
| `ephemeral` | `validate` | Cache, sessions, temp data |
| `standard` | `validate`, `authorize` | User profiles, posts |
| `critical` | `validate`, `authorize`, `audit`, `protect` | Payments, medical, legal |

---

## How It Works

EVOID is a **runtime**, not a framework. Adapters bridge the outside world:

```
External Event (HTTP, CLI, Telegram, WebSocket, ...)
        |
   Adapter converts event → Intent
        |
   Runtime executes Intent through Pipeline
        |
   Pipeline runs Processors (validate, authorize, audit, ...)
        |
   Result returned to Adapter → converted back to response
```

**Adapters** provide route decorators and event conversion. **Services** are Intent + handler registrations. **Pipelines** are processor chains chosen by intent level.

See [How It Works](https://evolvebeyond.github.io/EVOID/getting-started/architecture/) for the full picture.

---

## Quick Start

```bash
uv add evoid
evo init my-api && cd my-api
evo service new api && evo service run api
# http://0.0.0.0:8000
```

Or install optional engines:

```bash
evo install sqlite      # SQLite storage
evo install redis       # Redis cache
evo install pydantic    # Pydantic schema
evo install full        # Everything
```

---

## Three Syntax Styles

All IOP underneath. Pick your style:

### @route (function-based)

Route decorators come from the adapter. Switch adapters, same code:

```python
from evoid.adapters.asgi import get, post
from evoid.web.route import Service

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}
```

### @controller (class-based)

`@GET`, `@POST` mark routes. `@Controller` creates Intents from them:

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}
```

### Native (full control)

Explicit Intent creation. Adapter-agnostic — works with any transport:

```python
from evoid.native import create_service, on
from evoid import Intent, Level

app = create_service("my-api")

GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def get_user(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

on(app, GET_USER, get_user)
```

---

## Adapters

Each adapter converts its event type to Intents. Route decorators live in adapters because param extraction is adapter-specific:

| Adapter | Decorators | Install |
|:--------|:-----------|:--------|
| **ASGI** (HTTP) | `@get(path)`, `@post(path)` | `evoid[asgi]` |
| **Robyn** | `@get(app, path)`, `@post(app, path)` | `evoid[robyn]` |
| **Telegram** | `on(bot, event, handler)` | `evoid[telegram]` |
| **CLI** | `intent_from_args(cmd)` | built-in |
| **MCP** (AI agents) | `create_mcp_server(name)` | built-in |

See [Adapters](https://evolvebeyond.github.io/EVOID/learn/adapters/) for details and examples.

---

## Features

<table>
<tr>
<td>

**Zero Dependencies**
Core has no required packages

</td>
<td>

**AI Agent Integration**
Schema export + MCP server

</td>
<td>

**Plugin System**
PyPI + git install

</td>
</tr>
<tr>
<td>

**Python-Native Config**
Type-safe, composable

</td>
<td>

**Pipeline Hooks**
6 lifecycle events

</td>
<td>

**Testing System**
pytest + WebUI dashboard

</td>
</tr>
<tr>
<td>

**Async-Native**
Full async/await support

</td>
<td>

**Parallel Execution**
gather, parallel, IntentQueue

</td>
<td>

**Multi-Adapter**
ASGI, CLI, Telegram, WebSocket, MCP

</td>
</tr>
<tr>
<td>

**Storage Engines**
Memory, SQLite, Redis, Postgres

</td>
<td>

**Cache Engine**
LRU with TTL, Redis backend

</td>
<td>

**Extend Pipelines**
before/after processors, pipeline override

</td>
</tr>
</table>

---

## AI Agent Integration

```python
from evoid import export_schemas
from evoid.adapters.mcp import create_mcp_server

schemas = export_schemas()
server = create_mcp_server("my-api")
```

---

## Plugin System

```bash
evo plug install evoid-redis           # From PyPI
evo plug install git+https://...       # From git
evo plug search cache                  # Search PyPI
evo plug list                          # List installed
```

---

## Configuration

### Python (Recommended)

```python
from evoid.config import config

app = config(
    service={"name": "my-api"},
    runtime={"adapter": "asgi", "port": 8000},
    engines={"storage": "redis"},
)
```

### TOML

```toml
[service]
name = "my-api"

[engines]
storage = "redis"
```

---

## Testing

```python
from evoid.testing import tc
from myapp import GET_USER

def test_get_user():
    return tc(GET_USER, expect={"id": 1})
```

```bash
pytest tests/ -v                    # Run tests
pytest tests/ --evoid-webui         # With dashboard
pytest tests/ --evoid-inspect       # With pipeline traces
```

---

## Project Structure

```
my-api/
  evoid.toml              # TOML config (or evoid_config.py)
  shared/                 # Shared code
  services/
    api/
      main.py             # Service code
```

### Package Layout

```
evoid/
  core/          Intent, Pipeline, Context, Runtime, Events, MessageBus
  native/        IOP mother syntax (create_service, on)
  web/           @route and @controller syntax
  adapters/      asgi, cli, telegram, websocket, mcp, robyn
  engines/       storage, cache, auth, di, logger, metrics, schema, serializer
  processors/    Built-in processors (validate, authorize, etc.)
  config/        TOML + Python config loading
  testing/       pytest plugin + WebUI dashboard
  project/       Project scaffolding
```

---

## Documentation

**Full docs:** [https://evolvebeyond.github.io/EVOID/](https://evolvebeyond.github.io/EVOID/)

**Architecture:** [https://deepwiki.com/EvolveBeyond/EVOID](https://deepwiki.com/EvolveBeyond/EVOID)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork → Branch → Commit → PR
2. Tests: `pytest tests/ -v`
3. Lint: `ruff check evoid/`

---

## License

[Apache 2.0](LICENSE)

---

<p align="center">
  <img src="https://raw.githubusercontent.com/EvolveBeyond/EVOID/main/assets/evoid-footer.png" alt="EVOID" width="200">
  <br>
  <sub>Built with IOP principles. Intent is the platform.</sub>
</p>
