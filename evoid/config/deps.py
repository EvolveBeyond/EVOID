"""Dependency Map — Maps engine names to Python packages.

uv can read this to know what to install for each engine.
"""

# Engine → required packages
ENGINE_PACKAGES: dict[str, dict[str, list[str]]] = {
    # Schema engines
    "schema": {
        "native": [],  # No extra deps
        "pydantic": ["pydantic>=2.0.0,<3.0.0"],
        "msgspec": ["msgspec>=0.18.0,<0.20.0"],
        "attrs": ["attrs>=23.0.0,<25.0.0"],
    },

    # Storage engines
    "storage": {
        "memory": [],
        "sqlite": ["aiosqlite>=0.20.0,<0.21.0"],
        "sqlalchemy": ["sqlalchemy[asyncio]>=2.0.0,<3.0.0", "aiosqlite>=0.20.0,<0.21.0"],
        "redis": ["redis>=4.0.0,<5.0.0"],
        "postgres": ["asyncpg>=0.28.0,<0.30.0"],
        "mongo": ["motor>=3.0.0,<4.0.0"],
    },

    # Cache engines
    "cache": {
        "memory": [],
        "redis": ["redis>=4.0.0,<5.0.0"],
    },

    # Serializer engines
    "serializer": {
        "json": [],
        "msgspec": ["msgspec>=0.18.0,<0.20.0"],
        "orjson": ["orjson>=3.9.0,<4.0.0"],
    },

    # Logger engines
    "logger": {
        "structlog": ["structlog>=24.0.0,<25.0.0"],
        "loguru": ["loguru>=0.7.0,<0.8.0"],
    },

    # Metrics engines
    "metrics": {
        "simple": [],
        "prometheus": ["prometheus-client>=0.15.0,<1.0.0"],
    },

    # DI engines
    "di": {
        "native": [],
    },

    # Auth engines
    "auth": {
        "simple": [],
        "jwt": ["pyjwt>=2.10.0,<3.0.0"],
    },

    # Adapters
    "adapter": {
        "asgi": ["starlette>=0.27.0,<0.40.0", "uvicorn[standard]>=0.24.0,<0.25.0"],
        "robyn": ["robyn>=0.30.0,<1.0.0"],
        "telegram": ["aiogram>=3.0.0,<4.0.0"],
        "websocket": ["starlette>=0.27.0,<0.40.0"],
    },
}


def get_packages_for_config(engines: dict[str, str], adapter: str = "asgi") -> list[str]:
    """Get all required packages for a given config.

    Args:
        engines: Engine selections (e.g., {"schema": "pydantic", "storage": "redis"})
        adapter: Adapter name

    Returns:
        List of package specifications
    """
    packages = set()

    # Add adapter packages
    adapter_packages = ENGINE_PACKAGES.get("adapter", {}).get(adapter, [])
    packages.update(adapter_packages)

    # Add engine packages
    for engine_type, engine_name in engines.items():
        engine_packages = ENGINE_PACKAGES.get(engine_type, {}).get(engine_name, [])
        packages.update(engine_packages)

    return sorted(packages)


def generate_pyproject_extras() -> dict[str, list[str]]:
    """Generate pyproject.toml optional-dependencies from engine map.

    Returns dict suitable for [project.optional-dependencies]
    """
    extras = {}

    for engine_type, engines in ENGINE_PACKAGES.items():
        for engine_name, packages in engines.items():
            if packages:
                extra_name = f"{engine_type}-{engine_name}"
                extras[extra_name] = packages

    return extras
