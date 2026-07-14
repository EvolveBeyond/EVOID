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
    from evoid.project import list_services

    services = list_services(".")

    if not services:
        print("No services found.")
        sys.exit(1)

    print(f"Running {len(services)} services:")
    for svc in services:
        print(f"  - {svc.name} (port {svc.port})")

    # For now, run first service
    # TODO: Run all services concurrently
    cmd_service_run(services[0].name)


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


def main() -> None:
    """CLI entry point."""
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("evo — EVOID Runtime CLI")
        print()
        print("Project:")
        print("  evo init <name>              Create new project")
        print()
        print("Service:")
        print("  evo service new <name>       Add service to project")
        print("  evo service list             List services")
        print("  evo service run <name>       Run a service")
        print()
        print("Global:")
        print("  evo sync                     Sync dependencies")
        print("  evo run                      Run all services")
        print("  evo serve [host] [port]      Quick serve")
        print("  evo list-intents             List intents")
        print("  evo exec <intent>            Execute intent")
        print("  evo version                  Show version")
        return

    cmd = args[0]

    if cmd == "version":
        cmd_version()

    # Project commands
    elif cmd == "init":
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
    elif cmd == "run":
        cmd_run()
    elif cmd == "serve":
        host = args[1] if len(args) > 1 else "0.0.0.0"
        port = int(args[2]) if len(args) > 2 else 8000
        cmd_serve(host, port)
    elif cmd == "list-intents":
        cmd_list_intents()
    elif cmd == "list-processors":
        cmd_list_processors()
    elif cmd == "exec" and len(args) > 1:
        cmd_exec(args[1])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
