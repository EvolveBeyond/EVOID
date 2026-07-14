"""Full Stack IOP Example — Everything working together.

IOP: All code uses pure functions and data. No classes with behavior.
"""

import asyncio

from evoid.core import (
    Intent, Level, Service,
    register, execute, register_processor, Context,
    get_history,
)
from evoid.core.service import start, stop, on, call
from evoid.engines.logger import loguru as log
from evoid.engines.cache import memory as cache
from evoid.engines.storage import memory as storage
from evoid.engines.metrics import simple as metrics


# --- Intents (pure data) ---

CREATE_ORDER = Intent(name="create_order", level=Level.CRITICAL)
PROCESS_PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)
SEND_EMAIL = Intent(name="send_email", level=Level.STANDARD)
HEALTH_CHECK = Intent(name="health_check", level=Level.EPHEMERAL)


# --- Processors (pure functions) ---

async def validate(ctx: Context) -> dict:
    log.info(f"Validating: {ctx.intent.name}")
    metrics.increment("validated")
    return {"valid": True}

async def authorize(ctx: Context) -> dict:
    log.info(f"Authorizing: {ctx.intent.level.value}")
    metrics.increment("authorized")
    return {"authorized": True}

async def audit(ctx: Context) -> dict:
    log.info(f"Audit: {ctx.intent.name}")
    metrics.increment("audited")
    return {"audited": True}

async def protect(ctx: Context) -> dict:
    log.info(f"Protecting: {ctx.intent.level.value}")
    metrics.increment("protected")
    return {"protected": True}


# --- Register ---

register(CREATE_ORDER)
register(PROCESS_PAYMENT)
register(SEND_EMAIL)
register(HEALTH_CHECK)

register_processor("validate", validate)
register_processor("authorize", authorize)
register_processor("audit", audit)
register_processor("protect", protect)


# --- Services (pure data) ---

order_service = Service(name="order")
payment_service = Service(name="payment")
email_service = Service(name="email")


# --- Service handlers (pure functions) ---

async def handle_payment(intent: Intent) -> dict:
    log.info(f"Processing payment: {intent.metadata}")
    result = {"status": "success", "transaction_id": "txn_12345", "amount": intent.metadata.get("amount", 0)}
    await storage.write(f"payment:{result['transaction_id']}", result)
    await cache.set(f"payment:{result['transaction_id']}", result, ttl=300.0)
    metrics.increment("payments.processed")
    return result

async def handle_email(intent: Intent) -> dict:
    log.info(f"Sending email: {intent.metadata}")
    metrics.increment("emails.sent")
    return {"status": "sent"}


# --- Main ---

async def main():
    print("=" * 70)
    print("  EVOID Full Stack IOP Demo")
    print("=" * 70)

    log.init("evoid-demo", level="INFO")

    start(order_service)
    start(payment_service)
    start(email_service)

    on(payment_service, "process_payment", handle_payment)
    on(email_service, "send_email", handle_email)

    print("\n1. Direct Intent Execution:")
    result = await execute(HEALTH_CHECK)
    print(f"   Health: {result.success}")
    result = await execute(CREATE_ORDER)
    print(f"   Order: {result.success}")

    print("\n2. Inter-Service Communication:")
    payment_result = await call(payment_service, Intent(name="process_payment", level=Level.CRITICAL, metadata={"amount": 1999.98}))
    print(f"   Payment: {payment_result}")
    email_result = await call(email_service, Intent(name="send_email", level=Level.STANDARD, metadata={"to": "customer@example.com"}))
    print(f"   Email: {email_result}")

    print("\n3. Cache & Storage:")
    await cache.set("user:123", {"name": "Ali"}, ttl=300.0)
    cached = await cache.get("user:123")
    print(f"   Cached: {cached}")
    if payment_result:
        txn_id = payment_result["transaction_id"]
        stored = await storage.read(f"payment:{txn_id}")
        print(f"   Stored: {stored}")

    print("\n4. Metrics:")
    for name, value in metrics.all_metrics()["counters"].items():
        print(f"   {name}: {value}")

    print("\n5. Message History:")
    for msg in get_history():
        print(f"   [{msg.intent.level.value}] {msg.intent.name} (from: {msg.source})")

    stop(order_service)
    stop(payment_service)
    stop(email_service)

    print("\n" + "=" * 70)
    print("  Done!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
