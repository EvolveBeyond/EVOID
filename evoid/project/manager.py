"""Project Manager — Create and manage projects with multiple services.

IOP: Just data and functions. No classes with behavior.

Project structure:
my-project/
├── evoid.toml              # Project config
├── services/
│   ├── user-service/
│   │   ├── evoid.toml      # Service config
│   │   └── main.py
│   └── payment-service/
│       ├── evoid.toml
│       └── main.py
└── shared/
    └── models.py           # Shared models
"""

from __future__ import annotations

import tomli_w
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomli
except ImportError:
    import tomllib as tomli


# ============================================================
# Data structures
# ============================================================

@dataclass
class ServiceInfo:
    """Service info — pure data."""

    name: str
    path: Path
    port: int = 8000
    adapter: str = "asgi"
    engines: dict[str, str] = field(default_factory=dict)


@dataclass
class ProjectInfo:
    """Project info — pure data."""

    name: str
    path: Path
    services: list[ServiceInfo] = field(default_factory=list)


# ============================================================
# Project functions
# ============================================================

def init_project(name: str, path: str | Path = ".") -> ProjectInfo:
    """Create a new project.

    Creates:
    - <name>/evoid.toml (project config)
    - <name>/services/ (services directory)
    - <name>/shared/ (shared code)
    """
    project_path = Path(path) / name
    project_path.mkdir(parents=True, exist_ok=True)

    # Create directories
    (project_path / "services").mkdir(exist_ok=True)
    (project_path / "shared").mkdir(exist_ok=True)

    # Create project config
    config = {
        "project": {
            "name": name,
            "version": "0.1.0",
        },
        "runtime": {
            "adapter": "asgi",
            "host": "0.0.0.0",
        },
        "engines": {
            "schema": "native",
            "storage": "memory",
            "cache": "memory",
            "logger": "loguru",
        },
    }

    config_path = project_path / "evoid.toml"
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)

    # Create shared models
    shared_init = '''"""Shared models for all services."""

# Add shared Pydantic models here
'''
    (project_path / "shared" / "__init__.py").write_text(shared_init)

    return ProjectInfo(
        name=name,
        path=project_path,
    )


def add_service(
    project_path: str | Path,
    service_name: str,
    port: int = 8000,
) -> ServiceInfo:
    """Add a new service to a project.

    Creates:
    - services/<service_name>/evoid.toml
    - services/<service_name>/main.py
    """
    project = Path(project_path)
    service_path = project / "services" / service_name
    service_path.mkdir(parents=True, exist_ok=True)

    # Load project config for engine defaults
    project_config = _load_project_config(project)

    # Create service config
    config = {
        "service": {
            "name": service_name,
            "version": "0.1.0",
        },
        "runtime": {
            "adapter": project_config.get("runtime", {}).get("adapter", "asgi"),
            "host": "0.0.0.0",
            "port": port,
        },
        "engines": project_config.get("engines", {}),
        "pipeline": {
            "processors": ["validate"],
        },
    }

    config_path = service_path / "evoid.toml"
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)

    # Create service main.py
    main_py = f'''"""Service: {service_name}"""

from evoid.web.route import Service, get, post, run
from evoid.engines.logger import loguru as log


app = Service("{service_name}")


@app.get("/health")
async def health() -> dict:
    return {{"status": "healthy"}}


if __name__ == "__main__":
    log.init("{service_name}")
    import asyncio
    asyncio.run(run(app, port={port}))
'''
    (service_path / "main.py").write_text(main_py)

    return ServiceInfo(
        name=service_name,
        path=service_path,
        port=port,
    )


def list_services(project_path: str | Path) -> list[ServiceInfo]:
    """List all services in a project."""
    project = Path(project_path)
    services_dir = project / "services"

    if not services_dir.exists():
        return []

    services = []
    for service_dir in services_dir.iterdir():
        if service_dir.is_dir():
            config_path = service_dir / "evoid.toml"
            if config_path.exists():
                config = _load_service_config(config_path)
                services.append(ServiceInfo(
                    name=config.get("service", {}).get("name", service_dir.name),
                    path=service_dir,
                    port=config.get("runtime", {}).get("port", 8000),
                    adapter=config.get("runtime", {}).get("adapter", "asgi"),
                    engines=config.get("engines", {}),
                ))

    return services


def get_project_config(project_path: str | Path) -> dict[str, Any]:
    """Get project configuration."""
    return _load_project_config(Path(project_path))


# ============================================================
# Helpers
# ============================================================

def _load_project_config(project_path: Path) -> dict[str, Any]:
    """Load project config from evoid.toml."""
    config_path = project_path / "evoid.toml"
    if not config_path.exists():
        return {}

    with open(config_path, "rb") as f:
        return tomli.load(f)


def _load_service_config(config_path: Path) -> dict[str, Any]:
    """Load service config from evoid.toml."""
    with open(config_path, "rb") as f:
        return tomli.load(f)
