# Configuration

EVOID uses TOML for configuration.

## Service Configuration

```toml
# evoid.toml
[service]
name = "my-api"
version = "1.0.0"

[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000

[engines]
schema = "pydantic"
storage = "redis"
cache = "redis"
logger = "loguru"
```

## Sync Dependencies

```bash
evo sync
```

This reads your `evoid.toml` and installs required packages.

## Engine Selection

| Engine | Package | When to use |
|--------|---------|-------------|
| `schema = "pydantic"` | pydantic | Data validation |
| `storage = "redis"` | redis | Fast storage |
| `cache = "redis"` | redis | Distributed cache |
| `logger = "loguru"` | loguru | Beautiful logs |

## Configuration is the Composition Root 🎯

Changing infrastructure = changing config. Business logic untouched.

```toml
# Development
[engines]
storage = "memory"
cache = "memory"

# Production
[engines]
storage = "redis"
cache = "redis"
```

**Same code. Different engines. Just config change.** ✨
