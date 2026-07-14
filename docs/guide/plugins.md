# Plugin System

Register custom adapters, engines, and languages.

## Registering Plugins

```python
from evoid.engines.plugin.registry import register

# Register adapter
register(
    name="discord",
    plugin_type="adapter",
    factory=create_discord_adapter,
    version="1.0.0",
    description="Discord bot adapter",
)

# Register engine
register(
    name="redis",
    plugin_type="engine",
    factory=redis_storage,
    version="1.0.0",
    dependencies=("redis",),
)

# Register language runtime
register(
    name="rust",
    plugin_type="language",
    factory=rust_runtime,
    version="1.0.0",
)
```

## Resolving Plugins

```python
from evoid.engines.plugin.registry import resolve, list_plugins, has

# Resolve
adapter = resolve("discord", "adapter")

# List all
plugins = list_plugins()

# Check existence
if has("redis"):
    ...
```

## Loading from Config

```python
from evoid.engines.plugin.loader import from_config

config = {
    "plugins": {
        "engines": ["redis", "sqlalchemy"],
        "redis": {
            "module": "evoid.engines.storage.redis",
            "factory": "create_storage",
        },
    }
}

loaded = from_config(config)
```

## Loading from Module

```python
from evoid.engines.plugin.loader import from_module

plugin = from_module("my_package.my_plugin", plugin_type="engine")
```
