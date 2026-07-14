"""Extend Example — Inject new Intents and pipeline steps.

This example shows how to:
1. Add new Intents to an existing service
2. Add processors before/after existing ones
3. Override pipeline for specific Intents
"""

import asyncio

from evoid.core import Intent, Level, Context, execute
from evoid.core.extend import (
    add_intent,
    add_intent_with_pipeline,
    before,
    after,
    before_processor,
    after_processor,
    replace_pipeline,
    list_overrides,
)
from evoid.engines.logger import loguru as log


# ============================================================
# 1. Existing service with basic Intents
# ============================================================

PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)

async def validate_payment(ctx: Context) -> dict:
    log.info("Validating payment")
    return {"valid": True}

async def authorize_payment(ctx: Context) -> dict:
    log.info("Authorizing payment")
    return {"authorized": True}

async def process_payment(ctx: Context) -> dict:
    log.info("Processing payment")
    return {"status": "success"}


# Register existing service
from evoid.core import register, register_processor
register(PAYMENT)
register_processor("validate", validate_payment)
register_processor("authorize", authorize_payment)
register_processor("pay", process_payment)


# ============================================================
# 2. Extend: Add new Intent
# ============================================================

REFUND = Intent(name="refund_payment", level=Level.CRITICAL)

async def handle_refund(intent: Intent) -> dict:
    log.info(f"Processing refund: {intent.metadata}")
    return {"status": "refunded"}

# Add new Intent with handler
add_intent(REFUND, handle_refund)


# ============================================================
# 3. Extend: Add processor BEFORE existing one
# ============================================================

async def check_fraud(ctx: Context) -> dict:
    log.info("Checking for fraud")
    return {"fraud_checked": True}

# Add fraud check BEFORE authorize
before_processor("process_payment", "authorize", "check_fraud")

# Register the processor
register_processor("check_fraud", check_fraud)


# ============================================================
# 4. Extend: Add processor AFTER existing one
# ============================================================

async def send_receipt(ctx: Context) -> dict:
    log.info("Sending receipt")
    return {"receipt_sent": True}

# Add receipt sending AFTER pay
after_processor("process_payment", "pay", "send_receipt")

# Register the processor
register_processor("send_receipt", send_receipt)


# ============================================================
# 5. Extend: Add at beginning/end
# ============================================================

async def log_start(ctx: Context) -> dict:
    log.info("Pipeline started")
    return {"logged": True}

async def log_end(ctx: Context) -> dict:
    log.info("Pipeline ended")
    return {"logged": True}

# Add at beginning
before("process_payment", "log_start")
register_processor("log_start", log_start)

# Add at end
after("process_payment", "log_end")
register_processor("log_end", log_end)


# ============================================================
# 6. Extend: Replace entire pipeline
# ============================================================

CUSTOMPipeline = Intent(name="custom_pipeline", level=Level.STANDARD)

async def custom_handler(ctx: Context) -> dict:
    log.info("Custom pipeline executed")
    return {"custom": True}

# Replace pipeline completely
replace_pipeline("custom_pipeline", ["validate", "custom_handler", "send_receipt"])
add_intent(CUSTOMPipeline, custom_handler)


# ============================================================
# Demo
# ============================================================

async def main():
    print("=" * 60)
    print("  EVOID Extend Demo")
    print("=" * 60)

    log.init("evoid-extend", level="INFO")

    # Show pipeline overrides
    print("\n1. Pipeline Overrides:")
    print("-" * 40)
    for name, processors in list_overrides().items():
        print(f"  {name}: {' → '.join(processors)}")

    # Execute extended payment pipeline
    print("\n2. Execute Extended Payment Pipeline:")
    print("-" * 40)
    result = await execute(PAYMENT)
    print(f"  Result: {result.success}")
    print(f"  Processors: {result.processors}")

    # Execute refund
    print("\n3. Execute New Refund Intent:")
    print("-" * 40)
    result = await execute(REFUND)
    print(f"  Result: {result.value}")

    # Execute custom pipeline
    print("\n4. Execute Custom Pipeline:")
    print("-" * 40)
    result = await execute(CUSTOMPipeline)
    print(f"  Result: {result.processors}")

    print("\n" + "=" * 60)
    print("  Done!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
