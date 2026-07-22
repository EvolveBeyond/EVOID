"""Annotations — C#-like attributes for EVOID handlers.

IOP Principle: Decorators attach metadata. Runtime reads it.
No magic, no metaclasses — just function attributes.

Usage:
    from evoid.core.annotations import intent, requires, validates, rate_limit

    @intent(pipeline=("validate", "authorize", "process_payment"), timeout=30)
    @requires("auth_engine", "db_connection")
    @validates({"amount": {"type": "number", "required": True}})
    @rate_limit(max_calls=100, period=60)
    async def process_payment(ctx):
        ...
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def intent(
    pipeline: tuple[str, ...] | None = None,
    timeout: float | None = None,
    priority: int = 0,
    description: str = "",
) -> Callable:
    """Declare intent metadata on a handler.

    Args:
        pipeline: Explicit processor chain. If None, uses level defaults.
        timeout: Max execution time in seconds.
        priority: Execution ordering priority.
        description: Human-readable description.
    """
    def decorator(fn: Callable) -> Callable:
        fn._evoid_intent = {
            "pipeline": pipeline,
            "timeout": timeout,
            "priority": priority,
            "description": description,
        }
        return fn
    return decorator


def requires(*deps: str) -> Callable:
    """Declare required dependencies.

    The runtime checks these at registration time and logs warnings
    if any dependency is not available in the DI container.

    Usage:
        @requires("auth_engine", "db_connection")
        async def get_user(ctx):
            auth = ctx.deps["auth_engine"]
    """
    def decorator(fn: Callable) -> Callable:
        existing = getattr(fn, "_evoid_requires", ())
        fn._evoid_requires = (*existing, *deps)
        return fn
    return decorator


def validates(schema: dict[str, Any] | str) -> Callable:
    """Declare input validation schema.

    Args:
        schema: Dict of field definitions or a named schema reference string.

    Usage:
        @validates({"name": {"type": "string", "required": True}})
        async def create_user(ctx): ...

        @validates("UserSchema")  # reference by name
        async def create_user(ctx): ...
    """
    def decorator(fn: Callable) -> Callable:
        fn._evoid_validates = schema
        return fn
    return decorator


def rate_limit(max_calls: int, period: float) -> Callable:
    """Declare rate limiting.

    Args:
        max_calls: Maximum number of calls allowed in the period.
        period: Time window in seconds.

    Usage:
        @rate_limit(max_calls=100, period=60)
        async def api_call(ctx): ...
    """
    def decorator(fn: Callable) -> Callable:
        fn._evoid_rate_limit = {"max_calls": max_calls, "period": period}
        return fn
    return decorator


def apply_annotations(fn: Callable) -> dict[str, Any]:
    """Read all annotations from a handler and return config dict.

    Returns:
        {
            "pipeline": tuple[str, ...] | None,
            "timeout": float | None,
            "priority": int,
            "description": str,
            "requires": tuple[str, ...],
            "validates": dict | str | None,
            "rate_limit": dict | None,
        }
    """
    intent_data = getattr(fn, "_evoid_intent", {})
    return {
        "pipeline": intent_data.get("pipeline"),
        "timeout": intent_data.get("timeout"),
        "priority": intent_data.get("priority", 0),
        "description": intent_data.get("description", ""),
        "requires": getattr(fn, "_evoid_requires", ()),
        "validates": getattr(fn, "_evoid_validates", None),
        "rate_limit": getattr(fn, "_evoid_rate_limit", None),
    }


def validate_annotations(fn: Callable) -> list[str]:
    """Validate annotations on a handler. Returns list of error messages.

    Catches problems at registration time, not runtime.
    """
    errors: list[str] = []
    ann = apply_annotations(fn)
    fn_name = getattr(fn, "__name__", str(fn))

    # Check pipeline includes handler name
    if ann["pipeline"] is not None:
        if fn_name not in ann["pipeline"]:
            errors.append(
                f"Handler '{fn_name}' has explicit pipeline but its own name "
                f"is not in the pipeline. Add '{fn_name}' to the pipeline tuple."
            )

    # Validate rate_limit params
    rl = ann["rate_limit"]
    if rl is not None:
        if rl["max_calls"] <= 0:
            errors.append(f"rate_limit max_calls must be > 0, got {rl['max_calls']}")
        if rl["period"] <= 0:
            errors.append(f"rate_limit period must be > 0, got {rl['period']}")

    # Validate timeout
    if ann["timeout"] is not None and ann["timeout"] <= 0:
        errors.append(f"timeout must be > 0, got {ann['timeout']}")

    return errors
