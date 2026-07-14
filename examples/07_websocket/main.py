"""WebSocket Example — Real-time Intent-based communication.

This example shows how to create a WebSocket API using EVOID:
1. Define Intents
2. Create handlers
3. Run WebSocket server

Usage:
    python main.py

Then connect with:
    websocat ws://localhost:8000/ws

Requirements:
    pip install starlette uvicorn
"""

import json
from typing import Any

from evoid.core import Intent, Level, register
from evoid.adapters.websocket import create_ws_app, create_asgi_app
from evoid.engines.logger import loguru as log
from evoid.engines.cache import memory as cache


# ============================================================
# 1. Define Intents
# ============================================================

WS_MESSAGE = Intent(
    name="ws:message",
    level=Level.STANDARD,
)

WS_ECHO = Intent(
    name="ws:echo",
    level=Level.EPHEMERAL,
)

WS_BROADCAST = Intent(
    name="ws:broadcast",
    level=Level.STANDARD,
)


# ============================================================
# 2. Create App and Handlers
# ============================================================

ws_app = create_ws_app(name="evoid-ws")

# Store connected clients
clients: set = set()


@ws_app.on("connect")
async def handle_connect(intent: Intent) -> None:
    """Handle new connection."""
    log.info(f"Client connected: {intent.metadata.get('client')}")


@ws_app.on("message")
async def handle_message(intent: Intent) -> dict:
    """Handle incoming message."""
    data = intent.metadata.get("data", {})
    log.info(f"Received: {data}")

    # Echo back
    return {
        "type": "echo",
        "data": data,
    }


@ws_app.on("disconnect")
async def handle_disconnect(intent: Intent) -> None:
    """Handle disconnection."""
    log.info("Client disconnected")


# ============================================================
# 3. Run Server
# ============================================================

def main():
    """Run the WebSocket server."""
    log.init("evoid-ws", level="INFO")

    # Create ASGI app with WebSocket support
    asgi_app = create_asgi_app(ws_app)

    print("=" * 50)
    print("EVOID WebSocket Server")
    print("=" * 50)
    print()
    print("Endpoint: ws://localhost:8000/ws")
    print("Health: http://localhost:8000/health")
    print()
    print("Connect with:")
    print("  websocat ws://localhost:8000/ws")
    print()
    print("Send message:")
    print('  {"intent": "ws:echo", "data": {"hello": "world"}}')
    print()

    try:
        import uvicorn
        uvicorn.run(asgi_app, host="0.0.0.0", port=8000)
    except ImportError:
        print("Error: pip install uvicorn")


if __name__ == "__main__":
    main()
