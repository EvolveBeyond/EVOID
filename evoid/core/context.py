"""Context — Pure data. Isolated execution environment.

IOP Principle: Data carries its own intent.
Context is a mutable databag that processors read from and write to.
No methods, no behavior — just data.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .intent import Intent


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

    # Auto-generated
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


def fork(ctx: Context) -> Context:
    """Create a child context with same intent and deps."""
    return Context(
        intent=ctx.intent,
        state=ctx.state.copy(),
        deps=ctx.deps.copy(),
        metadata={**ctx.metadata, "parent_id": ctx.id},
    )
