# EVOID

**Reference Runtime for Intent-Oriented Programming**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4.1-orange.svg)](https://github.com/EvolveBeyond/EVOID)
[![Zero Dependencies](https://img.shields.io/badge/core%20deps-zero-brightgreen.svg)](https://github.com/EvolveBeyond/EVOID)
[![Tests](https://img.shields.io/badge/tests-33%20passing-brightgreen.svg)](https://github.com/EvolveBeyond/EVOID)

---

## What is IOP?

Every time you write an endpoint, you decide which database, how to cache, whether to encrypt, what priority. **IOP removes that burden.** Your data declares what it needs. The runtime handles how.

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}

@post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid", "amount": amount}
```

Three intent levels control infrastructure behavior:

| Level | Pipeline | Use Case |
|-------|----------|----------|
| `ephemeral` | `validate` | Cache, sessions, temp data |
| `standard` | `validate`, `authorize` | User profiles, posts |
| `critical` | `validate`, `authorize`, `audit`, `protect` | Payments, medical, legal |

---

## Install

```bash
uv add evoid
```

**Zero core dependencies.** Add only what you need:

```bash
evo install sqlite      # SQLite storage
evo install redis       # Redis cache
evo install pydantic    # Pydantic schema
evo install asgi        # ASGI adapter
evo install full        # Everything
```

Requires Python 3.12+.

---

## Quick Start

```bash
evo init my-api
cd my-api
evo service new api
evo service run api
# Server starts at http://0.0.0.0:8000
```

---

## Three Syntax Styles

All styles are IOP underneath. Pick the one that fits your team.

### @route (Function-based)

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created"}
```

### @controller (Class-based)

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created"}
```

### Native (Full Control)

```python
from evoid import Intent, Level, add_intent

MY_INTENT = Intent(name="get_user", level=Level.STANDARD)

async def handler(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

add_intent(MY_INTENT, handler)
```

---

## AI Agent Integration

EVOID exposes Intents as MCP tools for AI agents:

```python
from evoid import export_schemas
from evoid.adapters.mcp import create_mcp_server

# Export schemas for AI discovery
schemas = export_schemas()

# Create MCP server
server = create_mcp_server("my-api")
```

---

## Plugin System

### Install Plugins

```bash
evo plug install evoid-redis           # From PyPI
evo plug install git+https://...       # From git
evo plug search cache                  # Search PyPI
evo plug list                          # List installed
```

### Write Plugins

```python
# evoid_plugin.json
{
    "name": "evoid-redis",
    "version": "1.0.0",
    "type": "engine",
    "entry_point": "evoid_redis:register_plugin"
}
```

---

## Configuration

### Python (Recommended)

```python
# evoid_config.py
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

[runtime]
adapter = "asgi"
port = 8000

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
pytest tests/ -v                # Run tests
pytest tests/ --evoid-webui     # With dashboard
```

---

## CLI Reference

| Command | Alias | Description |
|---------|-------|-------------|
| `evo init <name>` | `i` | Create project |
| `evo service new <name>` | `s new` | Add service |
| `evo service list` | `s list` / `ls` | List services |
| `evo service run <name>` | `s run` | Run service |
| `evo run` | `r` | Run all services |
| `evo serve` | `sv` | Quick serve |
| `evo exec <intent>` | `e` | Execute intent |
| `evo list-intents` | `li` | List intents |
| `evo list-processors` | `lp` | List processors |
| `evo install <pkg>` | `ins` | Install optional dep |
| `evo plug install <name>` | `pl i` | Install plugin |
| `evo plug search <query>` | `pl s` | Search plugins |
| `evo plug list` | `pl l` | List installed |
| `evo version` | `v` | Show version |

---

## Project Structure

```
my-api/
  evoid_config.py       # Python config (or evoid.toml)
  shared/               # Shared code between services
  services/
    api/
      main.py           # Service code
```

---

## Features

| Feature | Description |
|---------|-------------|
| Intent-Driven | Data declares what, runtime decides how |
| Zero Dependencies | Core has no required packages |
| Python-Native Config | Type-safe, composable configuration |
| Plugin Standard | Publish plugins to PyPI with manifest |
| AI Agent Integration | Schema export + MCP server |
| Plugin Lifecycle Hooks | 6 events with security model |
| Async-Native | Full async/await support |
| Parallel Execution | Run multiple intents concurrently |
| Multi-Adapter | ASGI, CLI, Telegram, Robyn, WebSocket |
| Message Bus | Inter-service communication via Intents |
| Testing System | pytest plugin with WebUI dashboard |

---

## Documentation

**User docs:** [https://evolvebeyond.github.io/EVOID/](https://evolvebeyond.github.io/EVOID/)

**Architecture docs:** [https://deepwiki.com/EvolveBeyond/EVOID](https://deepwiki.com/EvolveBeyond/EVOID)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Commit your changes
4. Push and open a Pull Request

---

## License

Apache 2.0 — see [LICENSE](LICENSE)
