"""Web API Example — ASGI adapter with Intent-based routing.

This example shows how to create a web API using EVOID:
1. Define Intents
2. Create handlers
3. Run ASGI server

Usage:
    python main.py
    # Then visit http://localhost:8000/health
    # Or: curl -X POST http://localhost:8000/api/payment -d '{"amount": 99.99}'
"""

import asyncio
from dataclasses import dataclass

from evoid.core import Intent, Level, register, register_processor, Context
from evoid.engines.logger import loguru as log
from evoid.adapters.asgi import create_app, run


# ============================================================
# 1. Define Intents
# ============================================================

PAYMENT = Intent(
    name="post:/api/payment",
    level=Level.CRITICAL,
)

USER_CREATE = Intent(
    name="post:/api/users",
    level=Level.STANDARD,
)

USER_GET = Intent(
    name="get:/api/users",
    level=Level.STANDARD,
)

HEALTH = Intent(
    name="get:/health",
    level=Level.EPHEMERAL,
)


# ============================================================
# 2. Define Handlers
# ============================================================

async def handle_payment(intent: Intent) -> dict:
    """Handle payment creation."""
    data = intent.metadata.get("body", {})
    amount = data.get("amount", 0)

    log.info(f"Processing payment: {amount}")

    return {
        "status": "success",
        "transaction_id": "txn_12345",
        "amount": amount,
    }


async def handle_user_create(intent: Intent) -> dict:
    """Handle user creation."""
    data = intent.metadata.get("body", {})
    name = data.get("name", "Unknown")

    log.info(f"Creating user: {name}")

    return {
        "status": "created",
        "user": {
            "id": "user_001",
            "name": name,
        },
    }


async def handle_user_get(intent: Intent) -> dict:
    """Handle user retrieval."""
    log.info("Fetching users")

    return {
        "users": [
            {"id": "user_001", "name": "Ali"},
            {"id": "user_002", "name": "Sara"},
        ],
    }


# ============================================================
# 3. Register and Run
# ============================================================

# Register intents
register(PAYMENT)
register(USER_CREATE)
register(USER_GET)
register(HEALTH)

# Create handler mapping
handlers = {
    "post:/api/payment": handle_payment,
    "post:/api/users": handle_user_create,
    "get:/api/users": handle_user_get,
}


def main():
    """Run the web API."""
    log.init("evoid-api", level="INFO")

    print("=" * 50)
    print("EVOID Web API")
    print("=" * 50)
    print()
    print("Endpoints:")
    print("  GET  /health          - Health check")
    print("  POST /api/payment     - Create payment")
    print("  POST /api/users       - Create user")
    print("  GET  /api/users       - List users")
    print()
    print("Example:")
    print('  curl -X POST http://localhost:8000/api/payment \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"amount": 99.99}\'')
    print()

    run(
        name="evoid-api",
        handlers=handlers,
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
