"""Plugin Discovery — Find and install EVOID plugins from PyPI.

Naming convention: evoid-* or evoid-plugin-*
Discovery: Search PyPI for packages matching the pattern
Installation: uv add or pip install
"""

from __future__ import annotations

import subprocess
import sys
import json
from typing import Any

from .manifest import PluginManifest, load_manifest_from_module


def search_plugins(query: str = "evoid") -> list[dict[str, Any]]:
    """Search PyPI for EVOID plugins.

    Args:
        query: Search query (default: "evoid")

    Returns:
        List of plugin info dicts
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", query],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return _parse_pip_output(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return []


def discover_installed() -> list[PluginManifest]:
    """Discover all installed EVOID plugins.

    Scans installed packages for evoid_plugin.json manifests.
    """
    plugins = []

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            for pkg in packages:
                name = pkg.get("name", "")
                if name.startswith("evoid") and name != "evoid":
                    manifest = _try_load_manifest(name)
                    if manifest:
                        plugins.append(manifest)
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass

    return plugins


def install_plugin(name: str, use_uv: bool = True) -> bool:
    """Install an EVOID plugin.

    Args:
        name: Plugin package name (e.g., "evoid-redis")
        use_uv: Use uv if available, fallback to pip

    Returns:
        True if installation succeeded
    """
    import shutil

    if use_uv and shutil.which("uv"):
        cmd = [shutil.which("uv"), "add", name]
    else:
        cmd = [sys.executable, "-m", "pip", "install", name]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_plugin_info(name: str) -> dict[str, Any] | None:
    """Get info about a plugin from PyPI."""
    try:
        import urllib.request
        url = f"https://pypi.org/pypi/{name}/json"
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read())
    except Exception:
        return None


def _parse_pip_output(output: str) -> list[dict[str, Any]]:
    """Parse pip index versions output."""
    plugins = []
    for line in output.strip().split("\n"):
        if "evoid" in line.lower():
            parts = line.split()
            if parts:
                name = parts[0].rstrip(":")
                version = parts[1] if len(parts) > 1 else "unknown"
                plugins.append({"name": name, "version": version})
    return plugins


def _try_load_manifest(package_name: str) -> PluginManifest | None:
    """Try to load manifest from an installed package."""
    try:
        import importlib.metadata
        dist = importlib.metadata.distribution(package_name)
        # Look for evoid_plugin.json in the package
        for f in dist.files or []:
            if str(f).endswith("evoid_plugin.json"):
                # Found it — read from the dist location
                content = dist.read_text(str(f))
                if content:
                    import json
                    data = json.loads(content)
                    from .manifest import _parse_manifest
                    return _parse_manifest(data)
    except Exception:
        pass

    return None
