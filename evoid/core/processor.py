"""Processor — Type aliases for functions.

IOP Principle: Processors are independent Lego blocks.
A processor is just a function: context in → result out.
No classes, no protocols, no inheritance.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from .context import Context

# A processor is a function that takes Context and returns a result
Processor = Callable[[Context], Awaitable[Any]]


# Registry of processors — just a dict
_processors: dict[str, Processor] = {}


def register(name: str, fn: Processor) -> None:
    """Register a processor function."""
    _processors[name] = fn


def get(name: str) -> Processor | None:
    """Get a processor by name."""
    return _processors.get(name)


def all_processors() -> dict[str, Processor]:
    """Return all registered processors."""
    return _processors.copy()


def clear_processors() -> None:
    """Clear all registered processors."""
    _processors.clear()
