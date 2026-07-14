"""Robyn API Example — High-performance web API.

This example shows how to create a web API using Robyn + EVOID:
1. Define Intents
2. Create handlers
3. Run Robyn server

Usage:
    python main.py

Requirements:
    pip install robyn
"""

import json
from typing import Any

from evoid.core import Intent, Level, register
from evoid.adapters.robyn import create_app, run_app
from evoid.engines.logger import loguru as log
from evoid.engines.cache import memory as cache
from evoid.engines.metrics import simple as metrics


# ============================================================
# 1. Define Intents
# ============================================================

PAYMENT = Intent(
    name="POST:/api/payment",
    level=Level.CRITICAL,
)

USER_CREATE = Intent(
    name="POST:/api/users",
    level=Level.STANDARD,
)

USER_LIST = Intent(
    name="GET:/api/users",
    level=Level.STANDARD,
)


# ============================================================
# 2. Create App and Handlers
# ============================================================

app = create_app(name="evoid-robyn-api")


@app.post("/api/payment")
async def handle_payment(intent: Intent) -> dict:
    """Handle payment creation."""
    data = intent.metadata.get("body", {})
    amount = data.get("amount", 0)

    log.info(f"Processing payment: {amount}")
    metrics.increment("payments")

    result = {
        "status": "success",
        "transaction_id": "txn_12345",
        "amount": amount,
    }

    # Cache result
    await cache.set(f"payment:{result['transaction_id']}", result, ttl=300.0)

    return result


@app.post("/api/users")
async def handle_user_create(intent: Intent) -> dict:
    """Handle user creation."""
    data = intent.metadata.get("body", {})
    name = data.get("name", "Unknown")

    log.info(f"Creating user: {name}")
    metrics.increment("users.created")

    return {
        "status": "created",
        "user": {
            "id": "user_001",
            "name": name,
        },
    }


@app.get("/api/users")
async def handle_user_list(intent: Intent) -> dict:
    """Handle user listing."""
    log.info("Listing users")
    metrics.increment("users.listed")

    return {
        "users": [
            {"id": "user_001", "name": "Ali"},
            {"id": "user_002", "name": "Sara"},
        ],
    }


# ============================================================
# 3. Run Server
# ============================================================

def main():
    """Run the Robyn API."""
    log.init("evoid-robyn", level="INFO")

    print("=" * 50)
    print("EVOID Robyn API")
    print("=" * 50)
    print()
    print("Endpoints:")
    print("  POST /api/payment  - Create payment")
    print("  POST /api/users    - Create user")
    print("  GET  /api/users    - List users")
    print()
    print("Example:")
    print('  curl -X POST http://localhost:8000/api/payment \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"amount": 99.99}\'')
    print()

    run_app(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
