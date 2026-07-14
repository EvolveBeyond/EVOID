# Deployment

Deploy your EVOID application.

## Production Configuration

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

## Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY . .
RUN pip install -e .

CMD ["evo", "run"]
```

## Deploy to Cloud

### Railway

1. Push to GitHub
2. Connect to Railway
3. Auto-deploy

### Render

1. Push to GitHub
2. Create Web Service
3. Set build command: `pip install -e .`
4. Set start command: `evo run`

### Fly.io

```bash
fly launch
fly deploy
```

## Environment Variables

```python
import os

port = int(os.environ.get("PORT", 8000))
```

## Why Deploy? 🤔

- ✅ **Production ready** — EVOID is built for production
- ✅ **Cloud friendly** — Works anywhere Python runs
- ✅ **Docker support** — Container-ready
- ✅ **Scalable** — Handle millions of requests

**Deploy with confidence. EVOID handles the rest.** 🚀
