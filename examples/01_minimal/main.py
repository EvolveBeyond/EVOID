"""Minimal IOP Example — Full stack demo.

This example demonstrates:
1. Intent as data
2. Processors as functions
3. Pipeline composition
4. Config loading
5. Engine usage
"""

import asyncio

# Core IOP
from evoid.core import (
    Intent, Level, register, execute,
    register_processor, Context, Result,
)

# Engines
from evoid.engines.logger import structlog as logger
from evoid.engines.cache import memory as cache
from evoid.engines.metrics import simple as metrics

# Config
from evoid.config.loader import load as load_config


# --- Intents (pure data) ---

PAYMENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={"timeout": 30.0},
)

HEALTH = Intent(
    name="health_check",
    level=Level.EPHEMERAL,
)


# --- Processors (pure functions) ---

async def validate(ctx: Context) -> dict:
    """Validate intent data."""
    logger.info(f"Validating: {ctx.intent.name}")
    metrics.increment("validations")
    ctx.state["validated"] = True
    return {"status": "valid"}


async def authorize(ctx: Context) -> dict:
    """Check authorization."""
    logger.info(f"Authorizing: {ctx.intent.level.value}")
    metrics.increment("authorizations")
    ctx.state["authorized"] = True
    return {"authorized": True}


async def audit(ctx: Context) -> dict:
    """Log audit trail."""
    logger.info(f"Audit: {ctx.intent.name}")
    metrics.increment("audits")
    ctx.state["audited"] = True
    return {"audited": True}


async def protect(ctx: Context) -> dict:
    """Apply protection."""
    logger.info(f"Protecting: {ctx.intent.level.value}")
    metrics.increment("protections")
    ctx.state["protected"] = True
    return {"protected": True}


# --- Main ---

async def main():
    print("=" * 50)
    print("EVOID IOP Runtime Demo")
    print("=" * 50)

    # Load config
    config = load_config()
    print(f"\nConfig: {config.service.name} v{config.service.version}")
    print(f"Adapter: {config.runtime.adapter}")
    print(f"Engines: schema={config.engines.schema}, storage={config.engines.storage}")

    # Initialize logger
    logger.init("evoid-demo")

    # Register everything
    register(PAYMENT)
    register(HEALTH)
    register_processor("validate", validate)
    register_processor("authorize", authorize)
    register_processor("audit", audit)
    register_processor("protect", protect)

    # Cache demo
    await cache.set("demo", {"key": "value"}, ttl=60.0)
    cached = await cache.get("demo")
    print(f"\nCache test: {cached}")

    # Execute CRITICAL intent
    print("\n1. CRITICAL intent:")
    result = await execute(PAYMENT)
    print(f"   Result: success={result.success}")
    print(f"   Processors: {result.processors}")
    print(f"   Duration: {result.duration:.3f}s")

    # Execute EPHEMERAL intent
    print("\n2. EPHEMERAL intent:")
    result = await execute(HEALTH)
    print(f"   Result: success={result.success}")
    print(f"   Processors: {result.processors}")

    # Show metrics
    print("\nMetrics:")
    all_m = metrics.all_metrics()
    for name, value in all_m["counters"].items():
        print(f"  {name}: {value}")

    print("\n" + "=" * 50)
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
