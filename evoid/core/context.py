"""Context — Pure data. Isolated execution environment.

IOP Principle: Data carries its own intent.
Context is a mutable databag that processors read from and write to.
No methods, no behavior — just data.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

from .intent import Intent

# Fast ID generator — atomic counter + thread id, no uuid4 overhead
_counter = 0
_counter_lock = threading.Lock()


def _fast_id() -> str:
    global _counter
    with _counter_lock:
        _counter += 1
        return f"ctx-{_counter}-{threading.get_ident():x}"


@dataclass
class Context:
    """Execution context — pure data.

    Processors receive this, read what they need, write what they produce.
    The context never decides anything. It just holds data.
    """

    intent: Intent
    state: dict[str, Any] = field(default_factory=dict)
    deps: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[Exception] = field(default_factory=list)

    # Auto-generated — fast counter, no uuid4
    id: str = field(default_factory=_fast_id)


def fork(ctx: Context) -> Context:
    """Create a child context with same intent and deps."""
    return Context(
        intent=ctx.intent,
        state=ctx.state.copy(),
        deps=ctx.deps,
        metadata={**ctx.metadata, "parent_id": ctx.id},
    )
