"""Runtime — Composition of functions, not a class.

IOP Principle: Data carries its own intent.
The runtime is just a set of functions that compose together.
No class, no state — just data flow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .context import Context
from .intent import Intent, resolve as resolve_intent
from .pipeline import Result, execute as execute_pipeline
from .processor import Processor, all_processors
from .resolver import PipelineConfig, resolve_pipeline


@dataclass
class Config:
    """Runtime configuration — pure data."""

    name: str = "evoid-service"
    adapter: str = "asgi"
    engines: dict[str, str] = field(default_factory=dict)


async def execute(intent: Intent, config: Config | None = None) -> Result:
    """Execute an intent through the pipeline.

    This is THE core function. Everything else is composition.

    Pipeline resolution order:
    1. Check for user overrides (extend.py)
    2. Fall back to default resolution
    """
    # 1. Resolve intent → pipeline config (with overrides)
    from .extend import get_pipeline_config
    pipeline_config = get_pipeline_config(intent)

    # 2. Get processor registry
    registry = all_processors()

    # 3. Create context
    context = Context(intent=intent)

    # 4. Execute pipeline
    return await execute_pipeline(
        pipeline=pipeline_config.processors,
        context=context,
        registry=registry,
        timeout=pipeline_config.timeout,
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
