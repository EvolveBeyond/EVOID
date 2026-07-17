"""Adapters — Convert external events into Intents.

IOP: Adapters are the bridge between the outside world and Intent.
Every adapter produces the same internal execution model.

Available adapters:
- asgi: HTTP requests (Starlette/Uvicorn)
- cli: Command line arguments
- telegram: Telegram bot messages (aiogram)
- robyn: Robyn web framework
- websocket: WebSocket messages
"""

from .asgi import create_app as create_asgi_app
from .asgi import run as run_asgi
from .cli import intent_from_args
from .robyn import create_app as create_robyn_app
from .robyn import run_app as run_robyn
from .telegram import create_bot, run_bot
from .websocket import create_asgi_app as create_ws_asgi
from .websocket import create_ws_app

__all__ = [
    "create_asgi_app",
    "run_asgi",
    "intent_from_args",
    "create_bot",
    "run_bot",
    "create_robyn_app",
    "run_robyn",
    "create_ws_app",
    "create_ws_asgi",
]
