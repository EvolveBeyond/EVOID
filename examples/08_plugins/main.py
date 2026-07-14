"""Plugin System Example — Register custom adapters and engines.

This example demonstrates:
1. Registering custom plugins
2. Loading plugins from config
3. Using plugins in the runtime

Usage:
    python main.py
"""

from evoid.core import Intent, Level, register, execute, register_processor, Context
from evoid.engines.plugin.registry import (
    register as register_plugin,
    resolve,
    list_plugins,
    has,
)
from evoid.engines.plugin.loader import from_config
from evoid.engines.logger import loguru as log


# ============================================================
# 1. Register Custom Plugins
# ============================================================

# Register a custom adapter
register_plugin(
    name="discord",
    plugin_type="adapter",
    factory=lambda: print("Discord adapter created"),
    version="1.0.0",
    description="Discord bot adapter",
    author="EVOID Community",
)

# Register a custom storage engine
async def redis_read(key: str) -> str:
    return f"redis_value_for_{key}"

async def redis_write(key: str, value: str) -> bool:
    print(f"Redis: {key} = {value}")
    return True

register_plugin(
    name="redis",
    plugin_type="engine",
    factory={"read": redis_read, "write": redis_write},
    version="1.0.0",
    description="Redis storage engine",
    dependencies=("redis",),
)

# Register a custom language runtime
register_plugin(
    name="rust",
    plugin_type="language",
    factory={"compile": lambda: "Rust binary", "run": lambda: "Running Rust"},
    version="1.0.0",
    description="Rust language runtime",
)

# Register a custom processor
async def custom_validator(ctx: Context) -> dict:
    log.info("Custom validation running")
    return {"custom_valid": True}

register_plugin(
    name="custom-validator",
    plugin_type="processor",
    factory=custom_validator,
    version="1.0.0",
    description="Custom validation processor",
)


# ============================================================
# 2. Define Intents and Processors
# ============================================================

PAYMENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
)

async def validate(ctx: Context) -> dict:
    log.info("Standard validation")
    return {"valid": True}

async def process(ctx: Context) -> dict:
    log.info("Processing payment")
    return {"status": "success"}

register(PAYMENT)
register_processor("validate", validate)
register_processor("process", process)


# ============================================================
# 3. Demo
# ============================================================

async def main():
    print("=" * 60)
    print("  EVOID Plugin System Demo")
    print("=" * 60)

    log.init("evoid-plugins", level="INFO")

    # List all registered plugins
    print("\n1. Registered Plugins:")
    print("-" * 40)
    for plugin in list_plugins():
        print(f"  [{plugin.type:10}] {plugin.name} v{plugin.version}")
        if plugin.description:
            print(f"             {plugin.description}")

    # Resolve a plugin
    print("\n2. Resolve Plugins:")
    print("-" * 40)

    discord = resolve("discord", "adapter")
    print(f"  Discord adapter: {discord}")

    redis = resolve("redis", "engine")
    print(f"  Redis engine: {redis}")

    rust = resolve("rust", "language")
    print(f"  Rust runtime: {rust}")

    validator = resolve("custom-validator", "processor")
    print(f"  Custom validator: {validator}")

    # Check if plugin exists
    print("\n3. Plugin Existence:")
    print("-" * 40)
    print(f"  Has 'discord': {has('discord')}")
    print(f"  Has 'redis': {has('redis')}")
    print(f"  Has 'mysql': {has('mysql')}")

    # Load plugins from config
    print("\n4. Load from Config:")
    print("-" * 40)

    config = {
        "plugins": {
            "engines": ["my-custom-engine"],
            "my-custom-engine": {
                "module": "evoid.engines.storage.memory",
                "factory": "read",
                "version": "0.1.0",
            },
        }
    }

    loaded = from_config(config)
    print(f"  Loaded {len(loaded)} plugins from config")

    # Execute an intent
    print("\n5. Execute Intent:")
    print("-" * 40)

    result = await execute(PAYMENT)
    print(f"  Result: {result.success}")

    print("\n" + "=" * 60)
    print("  Plugin system demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
