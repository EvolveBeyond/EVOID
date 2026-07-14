"""Plugin Registry — Where plugins live.

IOP: Just dicts and functions. No classes with behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Callable, Awaitable


# Plugin types
PluginType = str  # "adapter", "engine", "language", "processor"

# Registry: plugin_type -> plugin_name -> plugin_factory
_registry: dict[PluginType, dict[str, Any]] = {
    "adapter": {},
    "engine": {},
    "language": {},
    "processor": {},
}


@dataclass(frozen=True)
class Plugin:
    """Plugin metadata — pure data."""

    name: str
    type: PluginType
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    dependencies: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


# Plugin metadata registry
_plugins: dict[str, Plugin] = {}


def register(
    name: str,
    plugin_type: PluginType,
    factory: Any,
    *,
    version: str = "0.1.0",
    description: str = "",
    author: str = "",
    dependencies: tuple[str, ...] = (),
    **metadata: Any,
) -> Plugin:
    """Register a plugin.

    Args:
        name: Unique plugin name (e.g., "telegram", "redis", "rust")
        plugin_type: Type of plugin ("adapter", "engine", "language", "processor")
        factory: The plugin implementation (class, function, or dict)
        version: Plugin version
        description: What this plugin does
        author: Plugin author
        dependencies: Required packages
        metadata: Extra info

    Returns:
        Plugin metadata

    Example:
        # Register an adapter
        register("telegram", "adapter", TelegramAdapter)

        # Register a storage engine
        register("redis", "engine", redis_storage)

        # Register a language runtime
        register("rust", "language", rust_runtime)
    """
    # Store factory
    _registry.setdefault(plugin_type, {})[name] = factory

    # Store metadata
    plugin = Plugin(
        name=name,
        type=plugin_type,
        version=version,
        description=description,
        author=author,
        dependencies=dependencies,
        metadata=metadata,
    )
    _plugins[name] = plugin

    return plugin


def resolve(name: str, plugin_type: PluginType | None = None) -> Any | None:
    """Resolve a plugin by name and optional type.

    Returns the plugin factory (class, function, or dict).
    """
    if plugin_type:
        return _registry.get(plugin_type, {}).get(name)

    # Search all types
    for type_registry in _registry.values():
        if name in type_registry:
            return type_registry[name]

    return None


def get_plugin(name: str) -> Plugin | None:
    """Get plugin metadata by name."""
    return _plugins.get(name)


def list_plugins(plugin_type: PluginType | None = None) -> list[Plugin]:
    """List all registered plugins, optionally filtered by type."""
    if plugin_type:
        return [p for p in _plugins.values() if p.type == plugin_type]
    return list(_plugins.values())


def has(name: str) -> bool:
    """Check if a plugin is registered."""
    return name in _plugins


def unregister(name: str) -> bool:
    """Unregister a plugin."""
    if name in _plugins:
        plugin = _plugins.pop(name)
        _registry.get(plugin.type, {}).pop(name, None)
        return True
    return False


def clear() -> None:
    """Clear all plugins."""
    for type_registry in _registry.values():
        type_registry.clear()
    _plugins.clear()
