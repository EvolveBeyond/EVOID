#!/usr/bin/env python3
"""
Auto-update AGENTS.md from source code.

Scans evoid/ source files and regenerates:
- AGENTS.md (architecture + coding conventions + agent instructions)

design.md and CONTEXT.md are manually maintained as contracts.
Triggered by pre-commit hook when any evoid/**/*.py file changes.
"""

import os
import re
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
EVOID_DIR = PROJECT_ROOT / "evoid"
TODAY = datetime.now().strftime("%Y-%m-%d")


def get_version() -> str:
    pyproject = PROJECT_ROOT / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
    return "unknown"


def scan_modules() -> Dict[str, List[str]]:
    """Scan evoid/ and return module structure {dir: [files]}."""
    modules = {}
    for py_file in sorted(EVOID_DIR.rglob("*.py")):
        rel = py_file.relative_to(EVOID_DIR)
        parent = str(rel.parent)
        if parent == ".":
            parent = "evoid/"
        else:
            parent = f"evoid/{parent}/"
        if parent not in modules:
            modules[parent] = []
        modules[parent].append(rel.name)
    return modules


def scan_classes() -> List[Tuple[str, str, str]]:
    """Scan for class definitions: [(module_path, class_name, docstring_first_line)]."""
    classes = []
    for py_file in EVOID_DIR.rglob("*.py"):
        try:
            content = py_file.read_text()
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            continue

        rel = str(py_file.relative_to(PROJECT_ROOT))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                first_line = doc.split("\n")[0].strip() if doc else ""
                classes.append((rel, node.name, first_line))
    return classes


def scan_decorators() -> Dict[str, List[str]]:
    """Scan for decorator usage: {decorator_name: [locations]}."""
    decorators = {}
    for py_file in EVOID_DIR.rglob("*.py"):
        try:
            content = py_file.read_text()
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            continue

        rel = str(py_file.relative_to(PROJECT_ROOT))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for dec in node.decorator_list:
                    name = ""
                    if isinstance(dec, ast.Name):
                        name = dec.id
                    elif isinstance(dec, ast.Attribute):
                        name = dec.attr
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Name):
                            name = dec.func.id
                        elif isinstance(dec.func, ast.Attribute):
                            name = dec.func.attr
                    if name:
                        decorators.setdefault(name, []).append(f"{rel}:{node.lineno}")
    return decorators


def generate_module_tree(modules: Dict[str, List[str]]) -> str:
    """Generate ASCII tree from module structure."""
    lines = []
    for dir_path, files in sorted(modules.items()):
        lines.append(f"├── {dir_path}")
        for f in sorted(files):
            lines.append(f"│   └── {f}" if f == sorted(files)[-1] else f"│   ├── {f}")
    return "\n".join(lines)


def update_agents_md(version: str, modules: Dict, classes: List, decorators: Dict):
    """Regenerate AGENTS.md with architecture + conventions + agent instructions."""
    tree = generate_module_tree(modules)

    class_table = "\n".join(
        f"| `{cls}` | `{loc.split('/')[-1]}` | {doc or '(no docstring)'} |"
        for loc, cls, doc in sorted(classes, key=lambda x: x[1])
        if not cls.startswith("_") and doc
    )

    dec_list = ", ".join(
        f"`@{name}` ({len(locs)} uses)"
        for name, locs in sorted(decorators.items(), key=lambda x: -len(x[1]))
        if len(locs) >= 2
    )

    content = f"""# EVOID - AI Agent Instructions & Architecture

> Auto-generated from source code. Do not edit manually.
> Last updated: {TODAY} | Source version: {version}

## Project Identity

- **Name:** EVOID (Evolutionary Intent-Oriented Lightweight Distribution)
- **Version:** {version}
- **Language:** Python 3.13+
- **Framework:** FastAPI + Uvicorn
- **Package Manager:** Rye (with hatchling build)
- **License:** Apache 2.0

## What This Project Does

EVOID is a microservices framework implementing Intent-Oriented Programming (IOP). Developers declare intents on Pydantic model fields, and the framework automatically applies appropriate infrastructure behavior: storage routing, caching, encryption, load shedding, and resilience patterns.

---

## Architecture Overview

### Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer                             │
│  evoid/cli/main.py (Typer)                              │
│  Commands: new, run, maintenance                         │
├─────────────────────────────────────────────────────────┤
│                Application Layer                         │
│  ServiceBuilder  │  Orchestrator  │  ProjectManager      │
│  (fluent API)    │  (multi-svc)   │  (project mgmt)      │
├─────────────────────────────────────────────────────────┤
│              Infrastructure Layer                        │
│  DI (HealthAware) │ PriorityQueue │ Auth (JWT)           │
│  Scheduler        │ Registry      │ PluginManager        │
│  Lifecycle        │ MessageBus    │ CacheLayer           │
├─────────────────────────────────────────────────────────┤
│                Data Layer (IOP Core)                     │
│  IntentSystem │ DataIO │ StorageProviders │ Persistence  │
│  IntentRouter │ ModelMapper │ Serialization (Fury)       │
├─────────────────────────────────────────────────────────┤
│            Monitoring / Intelligence Layer                │
│  EnvironmentalIntelligence │ PerformanceTracker          │
│  SystemMonitor (psutil)                                  │
└─────────────────────────────────────────────────────────┘
```

### Module Map

```
{tree}
```

### Data Flow: Request Lifecycle

```
1. HTTP Request arrives
2. Intent-Aware Middleware intercepts
   ├── Query IntentRegistry for route intent + priority
   ├── Query EnvironmentalIntelligence for SystemStatus
   └── Apply load shedding (PriorityQueue._is_request_allowed)
3. Request reaches handler function
4. DI Resolution (HealthAwareInject)
   ├── Check service health via BaseProvider.check_health()
   └── Return instance or HealthProxy (degraded mode)
5. Business logic executes
6. DataIO operations
   ├── Check CircuitBreaker state
   ├── Primary provider healthy?
   │   ├── YES → write to primary
   │   └── NO → CRITICAL? → EmergencySafetyBuffer
   │           OTHER? → fallback provider
   └── Record success/failure in CircuitBreaker
7. Response serialization (FuryCodec or JSON)
8. Return to client
```

### Dependencies

```
Core:     FastAPI, Uvicorn, Pydantic, HTTPX, PyJWT, psutil
Optional: PyFury (serialization), Redis (cache), asyncpg (Postgres), motor (Mongo)
Build:    Hatchling, Rye
Dev:      pytest, black, isort, flake8, mypy
```

---

## Codebase Rules

### DO
- Use Python 3.13+ syntax: `str | int` not `Union[str, int]`
- Use `Annotated[type, marker]` for type hints with metadata
- Keep business logic in `evoid/core/`, CLI thin in `evoid/cli/`
- Follow the fluent API pattern for ServiceBuilder
- Register intents via `IntentRegistry` when adding new endpoints
- Use `DataIO` for all storage operations (never direct provider access)
- Use `inject(ServiceType)` for dependency injection
- Handle errors via the `BaseError` hierarchy

### DON'T
- Don't use `Optional[X]` — use `X | None`
- Don't put business logic in CLI commands
- Don't access storage providers directly — go through `DataIO` or `PersistenceGateway`
- Don't hardcode intent behaviors — use `IntentResolver` and `BaseIntentConfig`
- Don't create new global singletons without registering them
- Don't skip health checks when injecting dependencies

---

## Coding Conventions

### Branch Names
Use short branch names (max 3 words, hyphen-separated). No slashes or type prefixes.

Examples: `intent-routing`, `fix-cache-ttl`, `add-redis-provider`

### Commits and PR Titles
Use conventional commit-style: `type(scope): summary`

Valid types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

Scopes: `core`, `cli`, `data`, `infra`, `intent`, `storage`, `cache`, `proxy`, `auth`

Examples:
- `feat(intent): add custom intent registration`
- `fix(data-io): handle emergency buffer overflow`
- `docs: update architecture documentation`

### Style Guide

#### Python Version
- Target: Python 3.13+
- Use `str | int` not `Union[str, int]`
- Use `X | None` not `Optional[X]`
- Use `Annotated[type, marker]` for metadata

#### Code Organization
- One class per file for core components
- Keep business logic in `evoid/core/`
- CLI (`evoid/cli/`) is a thin shell — no business logic
- Related utilities grouped in subdirectories

#### Naming
- Services: `kebab-case` (e.g., `user-service`)
- Python modules: `snake_case` (e.g., `service_builder.py`)
- Classes: `PascalCase` (e.g., `ServiceBuilder`)
- Intent names: `UPPER_CASE` (e.g., `CRITICAL`, `SQL_STORAGE`)

#### Functions
- Keep functions focused and small
- Prefer early returns over nested if/else
- Use `const` patterns (no mutable defaults)
- Async functions for I/O operations

#### Imports
- Standard library → third-party → local
- Use `TYPE_CHECKING` guard for circular import prevention
- Prefer absolute imports within the package

#### Error Handling
- All framework errors inherit from `BaseError`
- Use specific error types (e.g., `StorageError`, `IntentError`)
- Database errors go through `DBExceptionInterceptor`
- Never silently swallow exceptions

#### Testing
- Override dependencies with `override()` / `reset_overrides()`
- Test actual implementations, not mocks
- Unit tests for core logic, integration for I/O

---

## Architecture Principles

1. **Intent-First**: Data models declare infrastructure behavior
2. **Zero-Config Default**: Works out of the box with in-memory storage
3. **Health-Aware**: DI checks provider health on every resolution
4. **Resilient by Default**: Circuit breakers, emergency buffers, fallbacks
5. **CLI as Shell**: All business logic in core managers

## Key Patterns

### Service Registration
```python
svc = service("user-service").port(8000).build()
```

### Intent Declaration
```python
class UserProfile(BaseModel):
    name: critical(str)
    session: ephemeral(str)
```

### Dependency Injection
```python
db = inject(DatabaseService)
```

### Data Operations
```python
await data_io.write("key", data, Intent.CRITICAL)
```

---

## Key Classes ({len(classes)} total)

| Class | File | Purpose |
|-------|------|---------|
{class_table}

## Active Decorators

{dec_list}
"""
    (PROJECT_ROOT / "AGENTS.md").write_text(content)
    print(f"  ✓ AGENTS.md updated ({len(classes)} classes, {len(decorators)} decorators)")


def main():
    print("📄 Updating AGENTS.md from source code...")
    print(f"   Project: {PROJECT_ROOT}")
    print()

    version = get_version()
    print(f"   Version: {version}")

    # Scan source
    print("   Scanning modules...")
    modules = scan_modules()

    print("   Scanning classes...")
    classes = scan_classes()

    print("   Scanning decorators...")
    decorators = scan_decorators()

    print()
    print("   Generating docs...")

    update_agents_md(version, modules, classes, decorators)

    print()
    print("✅ AGENTS.md updated successfully!")
    print("   Note: design.md and CONTEXT.md are manually maintained contracts.")


if __name__ == "__main__":
    main()
