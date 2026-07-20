---
title: 'Production'
description: "Deploy, monitor, and scale Sandy's franchise."
---

# Production

Deploy, monitor, and scale Sandy's franchise.

## Production Config

!!! note "Scaling up?"
    This example uses built-in engines. For distributed caching (Redis) or advanced monitoring (Dashboard), install plugins:
    ```bash
    uv add evoid-redis        # Distributed caching
    uv add evoid-dashboard    # Monitoring UI
    ```

```toml
# evoid.toml
[project]
name = "sandy-franchise"
version = "1.0.0"

[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000

[engines]
schema = "native"
storage = "sqlite"
cache = "memory"
logger = "loguru"

[pipeline]
timeout = 10.0
```

## Running in Production

```bash
# With uvicorn
uvicorn my_app:app --host 0.0.0.0 --port 8000 --workers 4

# Or with evo CLI
evo service run sandy-franchise --host 0.0.0.0 --port 8000
```

## Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
EXPOSE 8000
CMD ["evo", "service", "run", "sandy-franchise"]
```

## Monitoring

```python
from evoid.core.pipeline import Result

async def monitor(intent: Intent) -> dict:
    """Track pipeline performance."""
    result = await execute(intent)

    # Log metrics
    print(f"Intent: {intent.name}")
    print(f"Duration: {result.duration:.3f}s")
    print(f"Processors: {len(result.processors)}")
    print(f"Success: {result.success}")

    return result.value
```

## Scaling

| Strategy | When |
|----------|------|
| Multiple workers | CPU-bound, single location |
| Multiple services | Different domains (orders, inventory) |
| Message Bus | Cross-service communication |
| Parallel execution | Batch processing |

## Health Checks

Add a health endpoint for load balancers and monitoring:

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service

app = Service("sandy-api")

@get("/health", level="ephemeral")
async def health() -> dict:
    return {"status": "healthy", "version": "1.0.0"}

@get("/ready", level="ephemeral")
async def readiness() -> dict:
    # Check database connection
    try:
        await db.execute("SELECT 1")
        return {"status": "ready", "database": "ok"}
    except Exception as e:
        return {"status": "not_ready", "database": str(e)}, 503
```

## Environment Config

Different configs for dev, staging, production:

```python
# config/development.py
from evoid.core.runtime import Config

config = Config(
    name="sandy-dev",
    adapter="asgi",
    engines={"storage": "memory", "cache": "memory"},
)

# config/production.py
config = Config(
    name="sandy-prod",
    adapter="asgi",
    engines={"storage": "sqlite", "cache": "memory"},
)
```

## Graceful Shutdown

Handle shutdown signals cleanly:

```python
import signal
import asyncio

shutdown_event = asyncio.Event()

def handle_shutdown(sig, frame):
    print("Shutting down...")
    shutdown_event.set()

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

# Wait for shutdown signal
await shutdown_event.wait()

# Cleanup: close DB connections, flush caches, etc.
await db.close()
cache.flush()
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Production config | Settings for real deployment |
| uvicorn / Docker | Running in production |
| Monitoring | Track performance and errors |
| Scaling strategies | Workers, services, parallelism |

## Next: What's Next

Let's recap Sandy's journey — [What's Next](whats-next.md).
