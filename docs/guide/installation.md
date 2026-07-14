# Installation

## Requirements

- Python 3.13+
- uv (recommended) or pip

## Install EVOID

```bash
# Using uv (recommended)
uv add evoid

# Using pip
pip install evoid
```

## Install with optional dependencies

```bash
# With Pydantic support
uv add "evoid[pydantic]"

# With ASGI adapter (FastAPI/Starlette)
uv add "evoid[asgi]"

# With Redis cache
uv add "evoid[redis]"

# With Loguru logging
uv add "evoid[loguru]"

# Full stack
uv add "evoid[full]"
```

## Verify installation

```bash
evo version
```
