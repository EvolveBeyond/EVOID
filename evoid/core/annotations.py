"""Annotations — C#-like attributes for EVOID handlers.

IOP Principle: Decorators attach metadata. Runtime reads it.
No magic, no metaclasses — just function attributes.

Usage:
    from evoid.core.annotations import intent, requires, validates, rate_limit, body, input

    @intent(pipeline=("validate", "authorize", "process_payment"), timeout=30)
    @requires("auth_engine", "db_connection")
    @validates({"amount": {"type": "number", "required": True}})
    @rate_limit(max_calls=100, period=60)
    @body(fields={"amount": {"type": "number", "required": True}})
    async def process_payment(ctx):
        ...
"""

from __future__ import annotations

import inspect
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


# ============================================================
# Input declaration decorators
# ============================================================

def body(
    fields: dict[str, Any] | None = None,
    optional: bool = False,
) -> Callable:
    """Declare that handler expects request body.

    Args:
        fields: Optional field schema for validation.
        optional: If True, handler works without body.

    Usage:
        @body()
        async def echo(body): return body

        @body(fields={"name": {"type": "string", "required": True}})
        async def create(name: str): return {"created": name}

        @body(optional=True)
        async def fire(data: dict = None): return {"ok": True}
    """
    def decorator(fn: Callable) -> Callable:
        fn._evoid_input = {
            "type": "body",
            "fields": fields,
            "optional": optional,
        }
        return fn
    return decorator


def params(
    fields: list[str] | None = None,
    optional: bool = False,
) -> Callable:
    """Declare that handler expects path/query parameters.

    Args:
        fields: Expected parameter names. None = accept all.
        optional: If True, handler works without params.

    Usage:
        @params(fields=["id"])
        async def get_user(id: str): return {"id": id}

        @params(optional=True)
        async def search(q: str = None): return {"q": q}
    """
    def decorator(fn: Callable) -> Callable:
        fn._evoid_input = {
            "type": "params",
            "fields": fields,
            "optional": optional,
        }
        return fn
    return decorator


def headers(
    required: list[str] | None = None,
    optional: list[str] | None = None,
) -> Callable:
    """Declare header requirements.

    Args:
        required: Headers that must be present.
        optional: Headers that may be present.

    Usage:
        @headers(required=["authorization"])
        async def secure(ctx): ...

        @headers(required=["x-api-key"], optional=["x-request-id"])
        async def api_call(ctx): ...
    """
    def decorator(fn: Callable) -> Callable:
        fn._evoid_input = {
            "type": "headers",
            "required": required or [],
            "optional": optional or [],
        }
        return fn
    return decorator


def _detect_input_from_signature(fn: Callable) -> dict[str, Any] | None:
    """Auto-detect input requirements from handler type hints.

    Returns input declaration dict, or None if no input needed.
    """
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())

    # Filter out 'ctx' and 'intent' params
    user_params = [
        p for p in params
        if p.name not in ("ctx", "intent", "self")
        and p.kind not in (inspect.Parameter.VAR_KEYWORD,)
    ]

    if not user_params:
        return None  # No input params → no body needed

    # Has explicit params → likely needs body
    return {"type": "auto", "params": [p.name for p in user_params]}


def apply_annotations(fn: Callable) -> dict[str, Any]:
    """Read all annotations from a handler and return config dict."""
    intent_data = getattr(fn, "_evoid_intent", {})
    input_data = getattr(fn, "_evoid_input", None)

    # Auto-detect if no explicit @body/@params
    if input_data is None:
        input_data = _detect_input_from_signature(fn)

    return {
        "pipeline": intent_data.get("pipeline"),
        "timeout": intent_data.get("timeout"),
        "priority": intent_data.get("priority", 0),
        "description": intent_data.get("description", ""),
        "requires": getattr(fn, "_evoid_requires", ()),
        "validates": getattr(fn, "_evoid_validates", None),
        "rate_limit": getattr(fn, "_evoid_rate_limit", None),
        "input": input_data,
    }


def validate_annotations(fn: Callable, method: str = "") -> list[str]:
    """Validate annotations on a handler. Returns list of error messages.

    Args:
        fn: Handler function to validate.
        method: HTTP method (GET, POST, etc.) for context-aware validation.
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

    # Validate input vs method
    inp = ann["input"]
    if inp is not None:
        method_upper = method.upper()

        # @body on GET → error (GET has no body)
        if inp.get("type") == "body" and method_upper == "GET":
            errors.append(
                f"Handler '{fn_name}' declares @body but is a GET route. "
                f"GET requests have no body. Use @params instead."
            )

        # @params on POST/PUT without @body → warning
        if inp.get("type") == "params" and method_upper in ("POST", "PUT", "PATCH"):
            errors.append(
                f"Handler '{fn_name}' declares @params on {method_upper} route. "
                f"POST/PUT typically need @body. Add @body if this handler expects a request body."
            )

    return errors
