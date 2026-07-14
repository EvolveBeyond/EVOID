"""Inter-Service Communication Example — Intent-based, no HTTP.

This example shows how services communicate directly:
1. Create service (pure data)
2. Register handlers
3. Call other services with Intents
4. No HTTP overhead. Direct function calls.
"""

import asyncio

from evoid.core import (
    Intent, Level, Service,
    register, Context,
)
from evoid.core.service import start, stop, on, call, emit
from evoid.engines.logger import loguru as log


# --- Services (pure data) ---

payment_service = Service(name="payment")
notification_service = Service(name="notification")
inventory_service = Service(name="inventory")


# --- Intent Definitions ---

PROCESS_PAYMENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={"timeout": 30.0},
)

SEND_NOTIFICATION = Intent(
    name="send_notification",
    level=Level.STANDARD,
)

CHECK_STOCK = Intent(
    name="check_stock",
    level=Level.STANDARD,
)


# --- Handlers (pure functions) ---

async def handle_payment(intent: Intent) -> dict:
    """Handle payment processing."""
    log.info(f"[payment] Processing: {intent.metadata}")
    await asyncio.sleep(0.01)
    return {"status": "success", "transaction_id": "txn_12345"}


async def handle_notification(intent: Intent) -> dict:
    """Handle notification sending."""
    log.info(f"[notification] Sending: {intent.metadata}")
    await asyncio.sleep(0.005)
    return {"status": "sent"}


async def handle_stock_check(intent: Intent) -> dict:
    """Handle stock check."""
    log.info(f"[inventory] Checking: {intent.metadata}")
    await asyncio.sleep(0.005)
    return {"product_id": "prod_001", "in_stock": True, "quantity": 42}


# --- Main ---

async def main():
    print("=" * 60)
    print("EVOID Inter-Service Communication Demo")
    print("=" * 60)

    log.init("evoid-services")

    # Register handlers (pure function calls)
    on(payment_service, "process_payment", handle_payment)
    on(notification_service, "send_notification", handle_notification)
    on(inventory_service, "check_stock", handle_stock_check)

    # Start services
    start(payment_service)
    start(notification_service)
    start(inventory_service)

    print("\n1. Direct service call (payment):")
    result = await call(
        payment_service,
        Intent(name="process_payment", level=Level.CRITICAL, metadata={"amount": 99.99}),
    )
    print(f"   Result: {result}")

    print("\n2. Direct service call (inventory):")
    result = await call(
        inventory_service,
        Intent(name="check_stock", level=Level.STANDARD, metadata={"product_id": "prod_001"}),
    )
    print(f"   Result: {result}")

    print("\n3. Emit to all subscribers:")
    await emit(
        payment_service,
        Intent(name="send_notification", level=Level.STANDARD, metadata={"message": "New order!"}),
    )
    await asyncio.sleep(0.1)

    # Stop services
    stop(payment_service)
    stop(notification_service)
    stop(inventory_service)

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
