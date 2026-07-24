"""Sync — Install dependencies and register pipelines based on evoid.toml.

IOP: Just functions that read config and run uv/pipeline registration.

Usage:
    evo sync                          # sync entire project (all services)
    evo sync --service game           # sync single service
    evo sync --show                   # show packages without installing
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .deps import get_packages_for_config
from .loader import load as load_config


def _find_uv() -> str:
    """Find uv binary. Returns path or raises SystemExit.

    Checks: PATH via shutil.which → Windows common paths → raises.
    """
    import shutil
    import platform

    # 1. Check PATH (works on all platforms)
    uv = shutil.which("uv")
    if uv:
        return uv

    # 2. Windows: check common install locations
    if platform.system() == "Windows":
        candidates = [
            Path.home() / ".local" / "bin" / "uv.exe",
            Path.home() / ".cargo" / "bin" / "uv.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "uv" / "uv.exe",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

    raise SystemExit(
        "uv not found. Install it:\n"
        "  Linux/macOS: curl -LsSf https://astral.sh/uv/install.sh | sh\n"
        "  Windows:     powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\""
    )


def _run_uv_add(packages: list[str], cwd: str | Path | None = None) -> bool:
    """Run uv add with packages."""
    if not packages:
        return True

    uv = _find_uv()
    cmd = [uv, "add"] + packages

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd,
        )
        if result.returncode == 0:
            return True
        else:
            print(f"  Error: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("Error: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def _collect_packages_from_config(config_path: Path) -> list[str]:
    """Collect all required packages from a single evoid.toml."""
    config = load_config(config_path)
    return get_packages_for_config(
        engines={
            "schema": config.engines.schema,
            "storage": config.engines.storage,
            "cache": config.engines.cache,
            "serializer": config.engines.serializer,
            "logger": config.engines.logger,
            "metrics": config.engines.metrics,
            "di": config.engines.di,
            "auth": config.engines.auth,
        },
        adapter=config.runtime.adapter,
    )


def _sync_pipeline(config_path: Path) -> None:
    """Register pipeline processors from evoid.toml."""
    config = load_config(config_path)
    processors = config.pipeline.processors

    if not processors:
        return

    print(f"  Pipeline processors: {', '.join(processors)}")

    # Import and register processors
    try:
        from evoid.core.processor import register as register_processor

        for proc_name in processors:
            # Try to import standard processors
            try:
                mod = __import__(f"evoid.processors.{proc_name}", fromlist=[proc_name])
                fn = getattr(mod, proc_name, None)
                if fn:
                    register_processor(proc_name, fn)
                    print(f"    ✓ registered: {proc_name}")
                else:
                    print(f"    ⚠ no function '{proc_name}' in module")
            except ImportError:
                print(f"    ⚠ processor '{proc_name}' not found (skipped)")
    except ImportError:
        print("    ⚠ evoid.processors not available (skipped)")


# ── Public API ───────────────────────────────────────────────────────────


def sync(config_path: str = "evoid.toml") -> bool:
    """Sync dependencies for a single config file.

    Reads evoid.toml, installs packages via uv, registers pipeline.
    """
    path = Path(config_path)
    if not path.exists():
        print(f"Config not found: {config_path}")
        return False

    config = load_config(path)
    name = config.service.name

    print(f"Syncing {name}...")

    # 1. Install packages
    packages = _collect_packages_from_config(path)
    if packages:
        print(f"  Installing {len(packages)} packages:")
        for pkg in packages:
            print(f"    - {pkg}")
        if not _run_uv_add(packages, cwd=path.parent):
            return False
    else:
        print("  No additional packages needed.")

    # 2. Register pipeline
    _sync_pipeline(path)

    print(f"  ✓ {name} synced.\n")
    return True


def sync_project(project_path: str = ".") -> bool:
    """Sync entire project — all services.

    Scans services/ directory for evoid.toml files.
    """
    project = Path(project_path)
    services_dir = project / "services"

    if not services_dir.exists():
        print(f"No services/ directory found in {project_path}")
        return False

    # Collect all packages from all services
    all_packages: set[str] = set()
    service_configs: list[Path] = []

    for service_dir in sorted(services_dir.iterdir()):
        if service_dir.is_dir():
            config_path = service_dir / "evoid.toml"
            if config_path.exists():
                service_configs.append(config_path)
                packages = _collect_packages_from_config(config_path)
                all_packages.update(packages)

    if not service_configs:
        print("No services with evoid.toml found.")
        return False

    print(f"Found {len(service_configs)} services.")

    # Install all packages at once
    if all_packages:
        sorted_packages = sorted(all_packages)
        print(f"Installing {len(sorted_packages)} unique packages:")
        for pkg in sorted_packages:
            print(f"  - {pkg}")
        if not _run_uv_add(sorted_packages, cwd=project):
            return False
    else:
        print("No additional packages needed.")

    # Register pipelines for each service
    for config_path in service_configs:
        _sync_pipeline(config_path)

    print(f"\n✓ Project synced ({len(service_configs)} services).")
    return True


def show_packages(config_path: str = "evoid.toml") -> None:
    """Show packages that would be installed."""
    path = Path(config_path)
    if not path.exists():
        print(f"Config not found: {config_path}")
        return

    config = load_config(path)
    packages = _collect_packages_from_config(path)

    print(f"Service: {config.service.name}")
    print(f"Adapter: {config.runtime.adapter}")
    print(f"Pipeline: {config.pipeline.processors}")
    print()

    if packages:
        print("Packages to install:")
        for pkg in packages:
            print(f"  {pkg}")
    else:
        print("No additional packages required.")
