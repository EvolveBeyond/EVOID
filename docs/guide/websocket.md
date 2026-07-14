# WebSocket Adapter

Real-time communication adapter.

## Basic Usage

```python
from evoid.adapters.websocket import create_ws_app, create_asgi_app
from evoid.core import Intent

# Create WebSocket app
ws_app = create_ws_app(name="ws-api")

# Register handlers
async def handle_message(intent: Intent) -> dict:
    data = intent.metadata.get("data", {})
    return {"echo": data}

ws_app.on("message", handle_message)

# Create ASGI app
asgi_app = create_asgi_app(ws_app)

# Run with uvicorn
import uvicorn
uvicorn.run(asgi_app, port=8000)
```

## Connect

```bash
websocat ws://localhost:8000/ws
```

## Send Message

```json
{"intent": "ws:echo", "data": {"hello": "world"}}
```
