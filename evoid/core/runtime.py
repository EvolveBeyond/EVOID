"""Runtime — Composition of functions, not a class.

IOP Principle: Data carries its own intent.
The runtime is just a set of functions that compose together.
No class, no state — just data flow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .context import Context
from .intent import Intent
from .intent import resolve as resolve_intent
from .pipeline import Result
from .pipeline import execute as execute_pipeline
from .processor import all_processors


@dataclass
class Config:
    """Runtime configuration — pure data."""
    name: str = "evoid-service"
    adapter: str = "asgi"
    engines: dict[str, str] = field(default_factory=dict)
    inspect: bool = False  # capture per-processor state


async def execute(intent: Intent, config: Config | None = None) -> Result:
    """Execute an intent through the pipeline."""
    from .extend import get_pipeline_config
    from .routing import apply_routing

    # 1. Resolve pipeline config (with overrides)
    pipeline_config = get_pipeline_config(intent)

    # 2. Apply routing rules
    pipeline = apply_routing(pipeline_config.processors, intent.name)

    # 3. Get processor registry
    registry = all_processors()

    # 4. Create context
    context = Context(intent=intent)

    # 5. Execute pipeline
    inspect = config.inspect if config else False
    return await execute_pipeline(
        pipeline=pipeline,
        context=context,
        registry=registry,
        timeout=pipeline_config.timeout,
        inspect=inspect,
    )


async def execute_by_name(name: str, **kwargs: Any) -> Result:
    """Execute an intent by name."""
    intent = resolve_intent(name)
    if intent is None:
        raise ValueError(f"Intent '{name}' not registered")

    if kwargs:
        intent = Intent(
            name=intent.name,
            level=intent.level,
            metadata={**intent.metadata, **kwargs},
            timeout=intent.timeout,
            priority=intent.priority,
        )

    return await execute(intent)
