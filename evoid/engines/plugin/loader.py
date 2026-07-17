"""Plugin Loader — Load plugins from config or files.

IOP: Just functions that load data and register plugins.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from .registry import Plugin, register


def from_config(config: dict[str, Any]) -> list[Plugin]:
    """Load plugins from TOML config data.

    Config format:
    ```toml
    [plugins]
    adapters = ["telegram", "discord"]
    engines = ["redis", "sqlalchemy"]
    languages = ["rust"]

    [plugins.telegram]
    module = "evoid.adapters.telegram"
    factory = "create_bot"

    [plugins.redis]
    module = "evoid.engines.storage.redis"
    factory = "create_storage"
    ```
    """
    plugins_config = config.get("plugins", {})
    loaded = []

    # Load listed plugins
    for plugin_type in ["adapter", "engine", "language", "processor"]:
        plugin_names = plugins_config.get(f"{plugin_type}s", [])
        for name in plugin_names:
            plugin_config = plugins_config.get(name, {})
            plugin = _load_plugin(name, plugin_type, plugin_config)
            if plugin:
                loaded.append(plugin)

    return loaded


def from_module(module_path: str, plugin_type: str = "engine") -> Plugin | None:
    """Load a plugin from a Python module.

    The module must have a `register_plugin()` function.
    """
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, "register_plugin"):
            return module.register_plugin()
        else:
            # Try to auto-register based on module contents
            return _auto_register(module, module_path, plugin_type)
    except ImportError as e:
        print(f"Failed to import {module_path}: {e}")
        return None


def from_file(file_path: str | Path) -> list[Plugin]:
    """Load plugins from a Python file.

    File must contain plugin registrations or register_plugin().
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return []

    # Add parent dir to path for imports
    import sys
    parent_dir = str(file_path.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    module_name = file_path.stem
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "register_plugins"):
            return module.register_plugins()
    except ImportError as e:
        print(f"Failed to load {file_path}: {e}")
    finally:
        if parent_dir in sys.path:
            sys.path.remove(parent_dir)

    return []


def _load_plugin(
    name: str,
    plugin_type: str,
    config: dict[str, Any],
) -> Plugin | None:
    """Load a single plugin from config."""
    module_path = config.get("module")
    factory_name = config.get("factory")

    if not module_path:
        return None

    try:
        module = importlib.import_module(module_path)

        if factory_name:
            factory = getattr(module, factory_name, None)
        else:
            # Try common names
            factory = (
                getattr(module, "create", None)
                or getattr(module, "create_" + plugin_type, None)
                or getattr(module, name, None)
                or module
            )

        return register(
            name=name,
            plugin_type=plugin_type,
            factory=factory,
            version=config.get("version", "0.1.0"),
            description=config.get("description", ""),
        )

    except ImportError as e:
        print(f"Failed to load plugin {name}: {e}")
        return None


def _auto_register(
    module: Any,
    module_path: str,
    plugin_type: str,
) -> Plugin | None:
    """Auto-register a module as a plugin."""
    # Find the main factory/function
    factory = (
        getattr(module, "create", None)
        or getattr(module, "app", None)
        or getattr(module, "handler", None)
    )

    if factory:
        name = module_path.split(".")[-1]
        return register(
            name=name,
            plugin_type=plugin_type,
            factory=factory,
            description=f"Auto-registered from {module_path}",
        )

    return None
