---
title: 'Deployment'
description: 'Deploy EVOID applications to production.'
---

# Deployment

Deploy EVOID applications to production.

## Quick Deploy

```bash
evo service run api
```

This starts the server at `http://0.0.0.0:8000`.

## Production Setup

### Uvicorn with Workers

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Worker count: `CPU cores * 2 + 1`

### Systemd Service

```ini
[Unit]
Description=EVOID API Service
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/opt/my-api
ExecStart=/opt/my-api/.venv/bin/evo service run api
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable my-api
sudo systemctl start my-api
```

### Docker

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv sync
COPY . .
EXPOSE 8000
CMD ["evo", "service", "run", "api"]
```

```bash
docker build -t my-api .
docker run -p 8000:8000 my-api
```

### Docker Compose

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
    restart: unless-stopped
```

## SSL / HTTPS

### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name myapi.example.com;

    ssl_certificate /etc/letsencrypt/live/myapi.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/myapi.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Health Check

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service

app = Service("my-api")

@get("/health", level="ephemeral")
async def health() -> dict:
    return {"status": "healthy"}
```

## Environment Variables

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
```

## Graceful Shutdown

```python
import signal
import sys

def shutdown(sig, frame):
    # Cleanup resources
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
```

## Monitoring

### Process Management

```bash
systemctl status my-api
journalctl -u my-api -f
systemctl restart my-api
```

### Metrics

```python
from evoid.engines.metrics import simple as metrics

metrics.increment("requests.total")
start = metrics.timer_start("request.duration")
# ... handle request
metrics.timer_stop("request.duration", start)
```

## Best Practices

- Use `level="ephemeral"` for health check endpoints
- Set appropriate timeouts per Intent level
- Use structured logging in production
- Monitor pipeline execution times
- Use the message bus for inter-service communication, not HTTP
