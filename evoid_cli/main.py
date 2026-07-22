"""EVO CLI — Command line interface for the runtime.

IOP: CLI is just an adapter that converts commands to Intents.
Short and elegant: evo (like the project is evolving)

Commands:
  evo init <name>              Create new project
  evo service new <name>       Add service to project
  evo service list             List services
  evo service run <name>       Run a service
  evo sync                     Sync dependencies
  evo run                      Run all services
  evo serve                    Quick serve
  evo list-intents             List intents
  evo exec <intent>            Execute intent
  evo version                  Show version
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from evoid.config.loader import load as load_config


def cmd_version() -> None:
    """Show version."""
    from evoid import __version__
    print(f"evo {__version__}")


# ============================================================
# Project commands
# ============================================================
# Project commands
# ============================================================

def cmd_init(name: str) -> None:
    """Create new project."""
    from evoid.project import init_project

    project = init_project(name)

    print(f"Created project: {name}/")
    print(f"  {name}/evoid.toml")
    print(f"  {name}/services/")
    print(f"  {name}/shared/")
    print()
    print(f"  cd {name}")
    print(f"  evo service new api")
    print(f"  evo service run api")


# ============================================================
# Service commands
# ============================================================

def cmd_service_new(service_name: str, port: int = 8000) -> None:
    """Add new service to project."""
    from evoid.project import add_service

    service = add_service(".", service_name, port)

    print(f"Created service: {service_name}/")
    print(f"  services/{service_name}/evoid.toml")
    print(f"  services/{service_name}/main.py")
    print()
    print(f"  evo service run {service_name}")


def cmd_service_list() -> None:
    """List services in project."""
    from evoid.project import list_services

    services = list_services(".")

    if not services:
        print("No services found. Create one with: evo service new <name>")
        return

    print("Services:")
    for svc in services:
        print(f"  {svc.name:<20} port={svc.port:<6} adapter={svc.adapter}")


def cmd_service_run(service_name: str) -> None:
    """Run a specific service."""
    from evoid.project import list_services

    services = list_services(".")
    service = next((s for s in services if s.name == service_name), None)

    if not service:
        print(f"Service '{service_name}' not found.")
        print("Available services:")
        for s in services:
            print(f"  {s.name}")
        sys.exit(1)

    # Load and run service config
    config = load_config(str(service.path / "evoid.toml"))

    print(f"Starting {service.name} on port {service.port}")

    from evoid.adapters.asgi import run
    run(
        name=service.name,
        host=config.runtime.host,
        port=service.port,
    )


# ============================================================
# Global commands
# ============================================================

def cmd_sync() -> None:
    """Sync all project dependencies."""
    from evoid.config.sync import sync
    sync("evoid.toml")


def cmd_run() -> None:
    """Run all services in project."""
    import asyncio
    from evoid.project import list_services

    services = list_services(".")

    if not services:
        print("No services found.")
        sys.exit(1)

    print(f"Running {len(services)} services:")
    for svc in services:
        print(f"  - {svc.name} (port {svc.port})")

    async def _run_all():
        import uvicorn
        from evoid.adapters.asgi import create_app

        servers = []
        for svc in services:
            config = load_config(str(svc.path / "evoid.toml"))
            app = create_app(name=svc.name)
            uconfig = uvicorn.Config(app, host=config.runtime.host, port=svc.port, log_level="info")
            server = uvicorn.Server(uconfig)
            servers.append(server)

        await asyncio.gather(*(s.serve() for s in servers))

    asyncio.run(_run_all())


def cmd_serve(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Quick serve (single service)."""
    from evoid.adapters.asgi import run
    run(name="evoid-service", host=host, port=port)


def cmd_list_intents() -> None:
    """List registered intents."""
    from evoid.core import all_intents
    intents = all_intents()
    if not intents:
        print("No intents registered.")
        return
    for name, intent in intents.items():
        print(f"  {name} [{intent.level.value}]")


def cmd_list_processors() -> None:
    """List registered processors."""
    from evoid.core import all_processors
    processors = all_processors()
    if not processors:
        print("No processors registered.")
        return
    for name in processors:
        print(f"  {name}")


def cmd_exec(intent_name: str) -> None:
    """Execute an intent by name."""
    from evoid.core import execute_by_name

    async def _exec():
        result = await execute_by_name(intent_name)
        if result.success:
            print(f"Success: {result.value}")
        else:
            print(f"Failed: {result.error}")
            sys.exit(1)
    asyncio.run(_exec())


def cmd_install(packages: list[str]) -> None:
    """Install optional dependencies or plugins."""
    import subprocess
    import shutil

    if not packages:
        print("Usage: evo install <package> [package...]")
        print()
        print("Built-in extras:")
        print("  sqlite        SQLite storage (aiosqlite)")
        print("  redis         Redis cache")
        print("  sqlalchemy    SQLAlchemy storage")
        print("  pydantic      Pydantic schema engine")
        print("  loguru        Loguru logger")
        print("  asgi          ASGI adapter (starlette + uvicorn)")
        print("  toml          TOML config support")
        print("  testing       Testing WebUI")
        print("  full          All optional dependencies")
        print()
        print("Plugins (from evoid-plugins):")
        print("  di            Dependency injection engine")
        print("  auth          Authentication & authorization")
        print("  tasks         Background tasks + logging")
        print("  smart-storage Multi-DB routing")
        print("  scylla        ScyllaDB/Cassandra storage")
        print("  dashboard     Monitoring dashboard")
        return

    # Built-in extras
    extras_map = {
        "sqlite": "sqlite", "redis": "redis", "sqlalchemy": "sqlalchemy",
        "pydantic": "pydantic", "loguru": "loguru", "asgi": "asgi",
        "robyn": "robyn", "telegram": "telegram", "toml": "toml",
        "testing": "testing", "full": "full",
    }

    # External plugins (evoid-plugins repo)
    plugins_map = {
        "di": "evoid-di",
        "auth": "evoid-auth",
        "tasks": "evoid-tasks",
        "smart-storage": "evoid-smart-storage",
        "scylla": "evoid-scylla",
        "dashboard": "evoid-dashboard",
    }

    extras = []
    plugins = []

    for pkg in packages:
        if pkg in extras_map:
            extras.append(extras_map[pkg])
        elif pkg in plugins_map:
            plugins.append(plugins_map[pkg])
        else:
            print(f"Unknown package: {pkg}")
            print(f"Extras: {', '.join(extras_map.keys())}")
            print(f"Plugins: {', '.join(plugins_map.keys())}")
            sys.exit(1)

    # Install extras
    if extras:
        spec = f"evoid[{','.join(extras)}]"
        print(f"Installing: {spec}")
        if shutil.which("uv"):
            cmd = [sys.executable, "-m", "uv", "add", spec]
        else:
            cmd = [sys.executable, "-m", "pip", "install", spec]
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"Failed to install extras")
            sys.exit(1)

    # Install plugins
    for plugin in plugins:
        print(f"Installing plugin: {plugin}")
        if shutil.which("uv"):
            cmd = [sys.executable, "-m", "uv", "add", plugin]
        else:
            cmd = [sys.executable, "-m", "pip", "install", plugin]
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"Failed to install plugin: {plugin}")
            sys.exit(1)

    result = subprocess.run(cmd, capture_output=False)
    if result.returncode == 0:
        print(f"\nInstalled: {spec}")
    else:
        print("\nInstallation failed")
        sys.exit(1)


def cmd_plug(args: list[str]) -> None:
    """Install EVOID plugins from PyPI or git."""
    import subprocess
    import shutil

    if not args:
        print("Usage: evo plug install <name|url>")
        print("       evo plug search <query>")
        print("       evo plug list")
        print()
        print("Examples:")
        print("  evo plug install evoid-redis       # From PyPI")
        print("  evo plug install git+https://...    # From git")
        print("  evo plug search cache               # Search PyPI")
        print("  evo plug list                       # List installed")
        return

    subcmd = args[0]

    if subcmd == "install":
        _plug_install(args[1:])
    elif subcmd == "search":
        _plug_search(args[1:])
    elif subcmd == "list":
        _plug_list()
    else:
        print(f"Unknown plug command: {subcmd}")
        sys.exit(1)


def _plug_install(args: list[str]) -> None:
    """Install a plugin."""
    import subprocess
    import shutil

    if not args:
        print("Usage: evo plug install <name|url>")
        print()
        print("Short names:")
        print("  di            evoid-di")
        print("  auth          evoid-auth")
        print("  tasks         evoid-tasks")
        print("  smart-storage evoid-smart-storage")
        print("  scylla        evoid-scylla")
        print("  dashboard     evoid-dashboard")
        return

    # Short name to full package mapping
    short_names = {
        "di": "evoid-di",
        "auth": "evoid-auth",
        "tasks": "evoid-tasks",
        "smart-storage": "evoid-smart-storage",
        "scylla": "evoid-scylla",
        "dashboard": "evoid-dashboard",
        "sqlite": "evoid-sqlite",
        "redis": "evoid-redis",
        "postgresql": "evoid-postgresql",
    }

    name = args[0]
    full_name = short_names.get(name, name)

    print(f"Installing plugin: {full_name}")

    if shutil.which("uv"):
        cmd = [sys.executable, "-m", "uv", "add", full_name]
    else:
        cmd = [sys.executable, "-m", "pip", "install", full_name]

    result = subprocess.run(cmd, capture_output=False)
    if result.returncode == 0:
        print(f"\nInstalled: {name}")
    else:
        print(f"\nFailed to install: {name}")
        sys.exit(1)


def _plug_search(args: list[str]) -> None:
    """Search for plugins on PyPI."""
    if not args:
        print("Usage: evo plug search <query>")
        return

    query = args[0]
    print(f"Searching PyPI for: {query}")

    try:
        from evoid.engines.plugin.discovery import search_plugins
        plugins = search_plugins(query)

        if not plugins:
            print(f"No plugins found for '{query}'")
            return

        print(f"\nFound {len(plugins)} plugins:")
        for p in plugins:
            print(f"  {p['name']:<30} {p.get('version', 'unknown')}")
    except Exception as e:
        print(f"Search failed: {e}")


def _plug_list() -> None:
    """List installed plugins."""
    try:
        from evoid.engines.plugin.discovery import discover_installed
        plugins = discover_installed()

        if not plugins:
            print("No EVOID plugins installed.")
            print("Install with: evo plug install <name>")
            return

        print(f"Installed plugins ({len(plugins)}):")
        for p in plugins:
            print(f"  {p.name:<30} {p.version:<10} {p.type}")
    except Exception as e:
        print(f"Failed to list plugins: {e}")


def main() -> None:
    """CLI entry point."""
    args = sys.argv[1:]

    # Short aliases
    aliases = {
        "i": "init", "s": "service", "ls": "service list",
        "r": "run", "sv": "serve", "v": "version",
        "li": "list-intents", "lp": "list-processors",
        "e": "exec", "ins": "install", "pl": "plug",
    }

    if not args or args[0] in ("-h", "--help"):
        print("evo — EVOID Runtime CLI")
        print()
        print("Project:               Aliases")
        print("  evo init <name>      i")
        print()
        print("Service:")
        print("  evo service new <name>       s new")
        print("  evo service list             s list / ls")
        print("  evo service run <name>       s run")
        print()
        print("Global:")
        print("  evo sync                     Sync dependencies")
        print("  evo run                      r — Run all services")
        print("  evo serve [host] [port]      sv — Quick serve")
        print("  evo list-intents             li — List intents")
        print("  evo list-processors          lp — List processors")
        print("  evo exec <intent>            e — Execute intent")
        print("  evo version                  v — Show version")
        print()
        print("Install & Plugins:")
        print("  evo install <pkg>            ins — Install optional dep")
        print("  evo install full             Install all optional deps")
        print("  evo plug install <name>      pl i — Install plugin")
        print("  evo plug search <query>      pl s — Search plugins")
        print("  evo plug list                pl l — List installed")
        return

    cmd = args[0]

    # Resolve alias
    if cmd in aliases:
        cmd = aliases[cmd]

    # Handle compound aliases (e.g., "s new" -> "service new")
    if cmd == "service" and len(args) > 1:
        subcmd = args[1]
        if subcmd in ("n", "new"):
            args = [args[0], "new"] + args[2:]
        elif subcmd in ("l", "list", "ls"):
            args = [args[0], "list"]
        elif subcmd in ("r", "run"):
            args = [args[0], "run"] + args[2:]

    # Handle "s" alias for service
    if cmd == "s" and len(args) > 1:
        args = ["service"] + args[1:]
        cmd = "service"

    if cmd == "version" or cmd == "v":
        cmd_version()

    # Project commands
    elif cmd == "init" or cmd == "i":
        if len(args) < 2:
            print("Usage: evo init <project-name>")
            sys.exit(1)
        cmd_init(args[1])

    # Service commands
    elif cmd == "service":
        if len(args) < 2:
            print("Usage: evo service <new|list|run> [args]")
            sys.exit(1)

        subcmd = args[1]

        if subcmd == "new":
            if len(args) < 3:
                print("Usage: evo service new <name> [port]")
                sys.exit(1)
            port = int(args[3]) if len(args) > 3 else 8000
            cmd_service_new(args[2], port)
        elif subcmd == "list":
            cmd_service_list()
        elif subcmd == "run":
            if len(args) < 3:
                print("Usage: evo service run <name>")
                sys.exit(1)
            cmd_service_run(args[2])
        else:
            print(f"Unknown service command: {subcmd}")
            sys.exit(1)

    # Global commands
    elif cmd == "sync":
        cmd_sync()
    elif cmd == "run" or cmd == "r":
        cmd_run()
    elif cmd == "serve" or cmd == "sv":
        host = args[1] if len(args) > 1 else "0.0.0.0"
        port = int(args[2]) if len(args) > 2 else 8000
        cmd_serve(host, port)
    elif cmd == "list-intents" or cmd == "li":
        cmd_list_intents()
    elif cmd == "list-processors" or cmd == "lp":
        cmd_list_processors()
    elif cmd == "exec" or cmd == "e":
        if len(args) < 2:
            print("Usage: evo exec <intent>")
            sys.exit(1)
        cmd_exec(args[1])
    elif cmd == "install" or cmd == "ins":
        cmd_install(args[1:])
    elif cmd == "plug" or cmd == "pl":
        cmd_plug(args[1:])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
