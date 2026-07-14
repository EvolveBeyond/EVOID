"""Auth Checker — Checks authorization.

IOP: Pure function. Uses auth engine from context deps.
"""

from __future__ import annotations

from typing import Any

from ..core.context import Context


async def process(ctx: Context) -> dict:
    """Check if request is authorized.

    Looks for auth engine in context dependencies.
    If no engine, skips auth check (returns authorized).
    """
    # Get auth engine from deps
    auth_engine = ctx.deps.get("auth_engine")

    if auth_engine is None:
        # No auth engine configured, skip check
        return {"authorized": True, "skipped": True}

    # Get token from metadata
    token = ctx.intent.metadata.get("token") or ctx.intent.metadata.get("headers", {}).get("authorization")

    if token is None:
        # No token provided
        return {"authorized": False, "reason": "no_token"}

    try:
        # Verify token using engine
        result = auth_engine.verify(token)
        if result:
            ctx.state["auth_info"] = result
            return {"authorized": True}
        else:
            return {"authorized": False, "reason": "invalid_token"}
    except Exception as e:
        return {"authorized": False, "reason": str(e)}
