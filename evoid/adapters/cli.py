"""CLI Adapter — Converts CLI commands to Intents.

IOP: Adapter is a function that maps data to Intent.
"""

from __future__ import annotations

from typing import Any

from ..core.intent import Intent, Level


def intent_from_args(
    command: str,
    args: list[str] | None = None,
    kwargs: dict[str, str] | None = None,
) -> Intent:
    """Convert CLI arguments to Intent.

    This is the adapter function — it maps CLI data to Intent.
    """
    # Determine level from flags
    level = Level.STANDARD
    if kwargs:
        if kwargs.get("critical"):
            level = Level.CRITICAL
        elif kwargs.get("ephemeral"):
            level = Level.EPHEMERAL

    return Intent(
        name=f"cli:{command}",
        level=level,
        metadata={
            "command": command,
            "args": args or [],
            "kwargs": kwargs or {},
        },
    )


def response_from_result(result: Any) -> str:
    """Convert pipeline result to CLI output."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return " ".join(f"{k}={v}" for k, v in result.items())
    return str(result)
