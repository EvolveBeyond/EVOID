"""Schema Validator — Validates data against schema.

IOP: Pure function. Uses schema engine from context deps.
"""

from __future__ import annotations

from ..core.context import Context


async def process(ctx: Context) -> dict:
    """Validate request data against schema.

    Looks for schema engine in context dependencies.
    If no engine, skips validation (returns valid).
    """
    # Get schema engine from deps
    schema_engine = ctx.deps.get("schema_engine")

    if schema_engine is None:
        # No schema engine configured, skip validation
        return {"validated": True, "skipped": True}

    # Get data to validate
    data = ctx.state.get("data") or ctx.intent.metadata.get("body", {})
    schema = ctx.state.get("schema") or ctx.intent.metadata.get("schema")

    if schema is None:
        # No schema defined, skip validation
        return {"validated": True, "skipped": True}

    try:
        # Validate using engine
        validated = schema_engine.validate(data, schema)
        ctx.state["validated_data"] = validated
        return {"validated": True}
    except Exception as e:
        return {"validated": False, "error": str(e)}
