# Plugin System

Register custom adapters, engines, and languages.

## Register a Plugin

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
```

## Resolve a Plugin

```python
from evoid.engines.plugin.registry import resolve

adapter = resolve("discord", "adapter")
```

## List All Plugins

```python
from evoid.engines.plugin.registry import list_plugins

plugins = list_plugins()
for plugin in plugins:
    print(f"{plugin.name} [{plugin.type}] v{plugin.version}")
```

## Load from Config

```python
from evoid.engines.plugin.loader import from_config

config = {
    "plugins": {
        "engines": ["redis", "sqlalchemy"],
    }
}

loaded = from_config(config)
```

## Why Plugins? 🤔

- ✅ **Extensible** — Add anything without modifying core
- ✅ **Replaceable** — Swap implementations easily
- ✅ **Testable** — Mock plugins for testing
- ✅ **Shareable** — Share plugins with community

**Everything is a plugin. That's the IOP way.** 🧩
