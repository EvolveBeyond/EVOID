"""Rate Limiter — Limits request rate.

IOP: Pure function. Simple in-memory rate limiting.
"""

from __future__ import annotations

import time

from ..core.context import Context

# Rate limit state: key -> (count, window_start)
_rate_limits: dict[str, tuple[int, float]] = {}

# Default limits: max requests per window (seconds)
_DEFAULT_LIMITS = {
    "ephemeral": (100, 60),   # 100 requests per minute
    "standard": (50, 60),     # 50 requests per minute
    "critical": (20, 60),     # 20 requests per minute
}


async def process(ctx: Context) -> dict:
    """Check rate limit for this request.

    Uses intent level to determine rate limit.
    """
    # Get rate limit key (user_id, IP, or intent name)
    key = (
        ctx.intent.metadata.get("user_id")
        or ctx.intent.metadata.get("headers", {}).get("x-forwarded-for")
        or ctx.intent.name
    )

    # Get limit for this intent level
    level = ctx.intent.level.value
    max_requests, window = _DEFAULT_LIMITS.get(level, (50, 60))

    # Check current count
    now = time.time()
    if key in _rate_limits:
        count, window_start = _rate_limits[key]
        if now - window_start < window:
            if count >= max_requests:
                return {"allowed": False, "reason": "rate_limit_exceeded"}
            _rate_limits[key] = (count + 1, window_start)
        else:
            # New window
            _rate_limits[key] = (1, now)
    else:
        _rate_limits[key] = (1, now)

    return {"allowed": True}
