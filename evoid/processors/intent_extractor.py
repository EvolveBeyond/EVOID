"""Intent Extractor — Extracts intent from request context.

IOP: Pure function. Extracts data from context.
"""

from __future__ import annotations

from typing import Any

from ..core.context import Context


async def process(ctx: Context) -> dict:
    """Extract intent metadata for downstream processors.

    This processor enriches the context with extracted intent information.
    """
    intent = ctx.intent

    # Extract and store intent info in state
    ctx.state["intent_name"] = intent.name
    ctx.state["intent_level"] = intent.level.value
    ctx.state["intent_priority"] = intent.priority
    ctx.state["intent_metadata"] = intent.metadata

    return {
        "extracted": True,
        "name": intent.name,
        "level": intent.level.value,
    }
