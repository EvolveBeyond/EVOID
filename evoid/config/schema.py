"""Config Schema — Python-native config with validation.

Two ways to configure EVOID:

1. TOML (evoid.toml) — traditional, human-readable
2. Python (evoid_config.py) — native, type-safe, intent-based

The Python config file IS the service definition.
It defines Intents, handlers, and infrastructure — all in one place.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .loader import EvoidConfig, ServiceConfig, RuntimeConfig, EnginesConfig, PipelineConfig


# ============================================================
# Python-native config builder
# ============================================================

def config(
    service: dict[str, Any] | None = None,
    runtime: dict[str, Any] | None = None,
    engines: dict[str, Any] | None = None,
    pipeline: dict[str, Any] | None = None,
) -> EvoidConfig:
    """Create config from Python dicts.

    Usage in evoid_config.py:
        from evoid.config import config

        app = config(
            service={"name": "my-api", "version": "1.0.0"},
            runtime={"adapter": "asgi", "port": 8000},
            engines={"storage": "redis", "cache": "memory"},
        )
    """
    return EvoidConfig(
        service=ServiceConfig(
            name=service.get("name", "evoid-service") if service else "evoid-service",
            version=service.get("version", "0.1.0") if service else "0.1.0",
        ),
        runtime=RuntimeConfig(
            adapter=runtime.get("adapter", "asgi") if runtime else "asgi",
            host=runtime.get("host", "0.0.0.0") if runtime else "0.0.0.0",
            port=runtime.get("port", 8000) if runtime else 8000,
        ),
        engines=EnginesConfig(
            schema=engines.get("schema", "native") if engines else "native",
            storage=engines.get("storage", "memory") if engines else "memory",
            cache=engines.get("cache", "memory") if engines else "memory",
            serializer=engines.get("serializer", "json") if engines else "json",
            di=engines.get("di", "native") if engines else "native",
            logger=engines.get("logger", "structlog") if engines else "structlog",
            metrics=engines.get("metrics", "simple") if engines else "simple",
            auth=engines.get("auth", "simple") if engines else "simple",
            options=engines.get("options", {}) if engines else {},
        ),
        pipeline=PipelineConfig(
            processors=pipeline.get("processors", ["validate", "authorize"]) if pipeline else ["validate", "authorize"],
        ),
    )


def load_config(path: str | Path | None = None) -> EvoidConfig:
    """Load config from file (TOML or Python).

    Auto-detects format:
    - evoid.toml → TOML (service-level)
    - pyproject.toml → TOML with [tool.evoid] (project-level)
    - evoid_config.py → Python
    - None → tries all
    """
    if path is not None:
        return _load_from_path(Path(path))

    # Try all formats
    toml_path = Path("evoid.toml")
    pyproject_path = Path("pyproject.toml")
    py_path = Path("evoid_config.py")

    if toml_path.exists():
        return _load_from_path(toml_path)
    elif pyproject_path.exists():
        return _load_from_pyproject(pyproject_path)
    elif py_path.exists():
        return _load_from_path(py_path)

    return EvoidConfig()  # Default config


def _load_from_pyproject(path: Path) -> EvoidConfig:
    """Load config from pyproject.toml [tool.evoid] section."""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            return EvoidConfig()

    with open(path, "rb") as f:
        data = tomllib.load(f)

    evoid_data = data.get("tool", {}).get("evoid", {})
    if not evoid_data:
        return EvoidConfig()

    return EvoidConfig(
        runtime=RuntimeConfig(
            adapter=evoid_data.get("adapter", "asgi"),
            host=evoid_data.get("host", "0.0.0.0"),
            port=evoid_data.get("port", 8000),
        ),
        engines=EnginesConfig(
            schema=evoid_data.get("engines", {}).get("schema", "native"),
            storage=evoid_data.get("engines", {}).get("storage", "memory"),
            cache=evoid_data.get("engines", {}).get("cache", "memory"),
            logger=evoid_data.get("engines", {}).get("logger", "structlog"),
        ),
    )


def _load_from_path(path: Path) -> EvoidConfig:
    """Load config from a specific file."""
    if path.suffix == ".toml":
        from .loader import load
        return load(path)
    elif path.suffix == ".py":
        return _load_python_config(path)
    else:
        return EvoidConfig()


def _load_python_config(path: Path) -> EvoidConfig:
    """Load config from a Python file."""
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("evoid_config", path)
    if spec is None or spec.loader is None:
        return EvoidConfig()

    module = importlib.util.module_from_spec(spec)
    sys.modules["evoid_config"] = module
    spec.loader.exec_module(module)

    # Look for 'app' or 'config' variable
    if hasattr(module, "app"):
        return module.app
    elif hasattr(module, "config"):
        return module.config

    return EvoidConfig()


# ============================================================
# Validation
# ============================================================

def validate_config(config: EvoidConfig) -> list[str]:
    """Validate a config. Returns list of errors (empty = valid)."""
    errors = []

    # Service
    if not config.service.name:
        errors.append("service.name is required")

    # Runtime
    valid_adapters = {"asgi", "cli", "telegram", "robyn", "websocket"}
    if config.runtime.adapter not in valid_adapters:
        errors.append(f"runtime.adapter must be one of {valid_adapters}")

    if not (1 <= config.runtime.port <= 65535):
        errors.append(f"runtime.port must be 1-65535 (got {config.runtime.port})")

    # Engines (including third-party plugins)
    valid_engines = {
        "schema": {"native", "pydantic", "msgspec", "attrs"},
        "storage": {"memory", "sqlite", "sqlalchemy", "redis", "postgres", "mongo", "scylla", "smart_storage"},
        "cache": {"memory", "redis"},
        "serializer": {"json", "msgspec", "orjson"},
        "di": {"native"},
        "logger": {"structlog", "loguru"},
        "metrics": {"simple", "prometheus"},
        "auth": {"simple", "jwt"},
    }

    engines_dict = {
        "schema": config.engines.schema,
        "storage": config.engines.storage,
        "cache": config.engines.cache,
        "serializer": config.engines.serializer,
        "di": config.engines.di,
        "logger": config.engines.logger,
        "metrics": config.engines.metrics,
        "auth": config.engines.auth,
    }

    for engine_name, value in engines_dict.items():
        valid = valid_engines.get(engine_name, set())
        if valid and value not in valid:
            errors.append(f"engines.{engine_name} must be one of {valid}")

    return errors
