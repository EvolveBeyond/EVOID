"""Logger Processor — Logs pipeline execution.

IOP: Pure function. Logs intent info.
"""

from __future__ import annotations

import time

from ..core.context import Context


async def process(ctx: Context) -> dict:
    """Log intent execution details.

    Stores timing info in context for final logging.
    """
    intent = ctx.intent

    # Store start time
    ctx.state["pipeline_start"] = time.time()

    # Log intent info
    level = intent.level.value
    name = intent.name

    return {
        "logged": True,
        "intent": name,
        "level": level,
    }


async def post_process(ctx: Context) -> dict:
    """Log pipeline completion.

    Called after pipeline completes (if registered).
    """
    start = ctx.state.get("pipeline_start")
    if start:
        duration = time.time() - start
        return {
            "duration": round(duration, 3),
            "intent": ctx.intent.name,
        }
    return {"duration": 0}
