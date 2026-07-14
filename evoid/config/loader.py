"""Config Loader — Reads evoid.toml configuration.

IOP: Just a function that reads TOML and returns data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class ServiceConfig:
    """Service configuration — pure data."""
    name: str = "evoid-service"
    version: str = "0.1.0"


@dataclass
class RuntimeConfig:
    """Runtime configuration — pure data."""
    adapter: str = "asgi"
    host: str = "0.0.0.0"
    port: int = 8000


@dataclass
class EnginesConfig:
    """Engine selections — pure data."""
    schema: str = "native"
    storage: str = "memory"
    cache: str = "memory"
    serializer: str = "json"
    di: str = "native"
    logger: str = "structlog"
    metrics: str = "simple"
    auth: str = "simple"


@dataclass
class PipelineConfig:
    """Pipeline configuration — pure data."""
    processors: list[str] = field(default_factory=lambda: [
        "validate", "authorize",
    ])


@dataclass
class EvoidConfig:
    """Complete EVOID configuration — pure data."""
    service: ServiceConfig = field(default_factory=ServiceConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    engines: EnginesConfig = field(default_factory=EnginesConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)


def load(path: str | Path = "evoid.toml") -> EvoidConfig:
    """Load configuration from TOML file.

    Returns default config if file not found.
    """
    path = Path(path)

    if not path.exists():
        return EvoidConfig()

    if tomllib is None:
        raise ImportError("tomli or tomllib required for config loading")

    with open(path, "rb") as f:
        data = tomllib.load(f)

    return _parse_config(data)


def _parse_config(data: dict[str, Any]) -> EvoidConfig:
    """Parse raw TOML data into EvoidConfig."""
    service_data = data.get("service", {})
    runtime_data = data.get("runtime", {})
    engines_data = data.get("engines", {})
    pipeline_data = data.get("pipeline", {})

    return EvoidConfig(
        service=ServiceConfig(
            name=service_data.get("name", "evoid-service"),
            version=service_data.get("version", "0.1.0"),
        ),
        runtime=RuntimeConfig(
            adapter=runtime_data.get("adapter", "asgi"),
            host=runtime_data.get("host", "0.0.0.0"),
            port=runtime_data.get("port", 8000),
        ),
        engines=EnginesConfig(
            schema=engines_data.get("schema", "native"),
            storage=engines_data.get("storage", "memory"),
            cache=engines_data.get("cache", "memory"),
            serializer=engines_data.get("serializer", "json"),
            di=engines_data.get("di", "native"),
            logger=engines_data.get("logger", "structlog"),
            metrics=engines_data.get("metrics", "simple"),
            auth=engines_data.get("auth", "simple"),
        ),
        pipeline=PipelineConfig(
            processors=pipeline_data.get("processors", ["validate", "authorize"]),
        ),
    )
