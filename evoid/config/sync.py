"""Sync — Install dependencies based on evoid.toml config.

IOP: Just a function that reads config and runs uv.
"""

from __future__ import annotations

import subprocess
import sys

from .deps import get_packages_for_config
from .loader import load as load_config


def sync(config_path: str = "evoid.toml") -> bool:
    """Sync dependencies based on config.

    Reads evoid.toml, determines required packages,
    and installs them via uv.

    Returns True on success.
    """
    config = load_config(config_path)

    # Get required packages
    packages = get_packages_for_config(
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

    if not packages:
        print("No additional packages required.")
        return True

    print(f"Installing {len(packages)} packages for {config.service.name}:")
    for pkg in packages:
        print(f"  - {pkg}")

    # Run uv add
    try:
        result = subprocess.run(
            [sys.executable, "-m", "uv", "add"] + packages,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("\nDependencies installed successfully!")
            return True
        else:
            print(f"\nError installing packages:\n{result.stderr}")
            return False

    except FileNotFoundError:
        print("Error: uv not found. Install with: pip install uv")
        return False


def show_packages(config_path: str = "evoid.toml") -> None:
    """Show packages that would be installed."""
    config = load_config(config_path)

    packages = get_packages_for_config(
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

    print(f"Packages for {config.service.name}:")
    print(f"  Adapter: {config.runtime.adapter}")
    print()
    for pkg in packages:
        print(f"  {pkg}")
