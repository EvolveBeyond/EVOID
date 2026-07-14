"""Processors Example — Using built-in processors.

This example shows how to:
1. Use built-in processors in pipeline
2. Extend pipeline with processors
3. Use rate limiting and circuit breaker
"""

import asyncio

from evoid.core import Intent, Level, Context, execute, register, register_processor
from evoid.core.extend import add_intent_with_pipeline
from evoid.processors import (
    intent_extractor,
    schema_validator,
    auth_checker,
    rate_limiter,
    circuit_breaker,
    logger_processor,
)
from evoid.processors.circuit_breaker import record_success, record_failure, get_state
from evoid.engines.logger import loguru as log


# ============================================================
# 1. Register processors
# ============================================================

register_processor("intent_extractor", intent_extractor)
register_processor("schema_validator", schema_validator)
register_processor("auth_checker", auth_checker)
register_processor("rate_limiter", rate_limiter)
register_processor("circuit_breaker", circuit_breaker)
register_processor("logger_processor", logger_processor)


# ============================================================
# 2. Define Intents with custom pipelines
# ============================================================

# Payment: full pipeline with all processors
PAYMENT = Intent(name="process_payment", level=Level.CRITICAL, metadata={"timeout": 30.0})

add_intent_with_pipeline(
    PAYMENT,
    processors=[
        "intent_extractor",
        "logger_processor",
        "rate_limiter",
        "circuit_breaker",
        "auth_checker",
        "schema_validator",
    ],
)

# Health check: minimal pipeline
HEALTH = Intent(name="health_check", level=Level.EPHEMERAL)

async def handle_health(ctx: Context) -> dict:
    return {"status": "healthy"}

register(HEALTH)
register_processor("health_check", handle_health)


# ============================================================
# 3. Demo
# ============================================================

async def main():
    print("=" * 60)
    print("  EVOID Processors Demo")
    print("=" * 60)

    log.init("evoid-processors", level="INFO")

    # Execute payment with full pipeline
    print("\n1. Payment (full pipeline):")
    print("-" * 40)
    result = await execute(PAYMENT)
    print(f"  Result: {result.success}")
    print(f"  Processors: {result.processors}")
    print(f"  Duration: {result.duration:.3f}s")

    # Execute health check
    print("\n2. Health check (minimal):")
    print("-" * 40)
    result = await execute(HEALTH)
    print(f"  Result: {result.value}")

    # Test rate limiting
    print("\n3. Rate limiting:")
    print("-" * 40)
    for i in range(3):
        result = await execute(PAYMENT)
        print(f"  Request {i+1}: {result.success}")

    # Test circuit breaker
    print("\n4. Circuit breaker:")
    print("-" * 40)
    for i in range(5):
        record_failure("payment_service")
        state = get_state("payment_service")
        print(f"  Failure {i+1}: state={state['state']}, failures={state['failures']}")

    # Reset circuit breaker
    record_success("payment_service")
    state = get_state("payment_service")
    print(f"  After success: state={state['state']}")

    print("\n" + "=" * 60)
    print("  Done!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
