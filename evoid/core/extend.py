"""Extend — Inject new Intents and pipeline steps into services.

IOP: Extension is just data manipulation.
No classes with behavior — just functions that modify registries.

Users can:
1. Add new Intents to a service
2. Add processors before/after existing ones
3. Override pipeline for specific Intents
4. Hook into lifecycle events
"""

from __future__ import annotations

from collections.abc import Callable

from .intent import Intent, Level
from .intent import register as register_intent
from .processor import register as register_processor
from .resolver import _DEFAULT_PROCESSORS, PipelineConfig, resolve_pipeline

# ============================================================
# 1. Add new Intent to a service
# ============================================================

def add_intent(intent: Intent, handler: Callable) -> None:
    """Add a new Intent with its handler.

    Automatically composes pipeline: [intent.name].
    Override with replace_pipeline() after calling this.

    Usage:
        from evoid.core import Intent, Level
        from evoid.core.extend import add_intent

        NEW_FEATURE = Intent(
            name="new_feature",
            level=Level.STANDARD,
            metadata={"description": "My new feature"},
        )

        async def handle_new_feature(intent: Intent) -> dict:
            return {"status": "implemented"}

        add_intent(NEW_FEATURE, handle_new_feature)
    """
    register_intent(intent)
    register_processor(intent.name, handler)
    # Auto-compose pipeline so handler actually runs
    _pipeline_overrides[intent.name] = PipelineConfig(
        processors=(intent.name,),
        priority=intent.priority,
    )


def add_intent_with_pipeline(
    intent: Intent,
    processors: list[str | Callable],
    handler: Callable | None = None,
) -> None:
    """Add a new Intent with custom pipeline.

    Processors can be strings (registered processor names) or callables
    (handler functions registered automatically under their __name__).

    Usage:
        add_intent_with_pipeline(
            Intent(name="complex_op", level=Level.CRITICAL),
            processors=["validate", transform_func, "save", notify_func],
            handler=my_handler,
        )
    """
    register_intent(intent)

    # Process mixed list: strings + callables
    resolved: list[str] = []
    for p in processors:
        if callable(p):
            name = getattr(p, "__name__", str(p))
            register_processor(name, p)
            resolved.append(name)
        else:
            resolved.append(p)

    # Register handler if provided
    if handler:
        register_processor(intent.name, handler)
        if intent.name not in resolved:
            resolved.append(intent.name)

    _pipeline_overrides[intent.name] = PipelineConfig(
        processors=tuple(resolved),
        priority=intent.priority,
        timeout=intent.metadata.get("timeout"),
    )


# ============================================================
# 2. Extend existing pipelines
# ============================================================

# Pipeline overrides: intent_name → PipelineConfig
_pipeline_overrides: dict[str, PipelineConfig] = {}


def before(intent_name: str, processor_name: str) -> None:
    """Add a processor BEFORE the first processor in pipeline.

    Usage:
        before("process_payment", "validate_payment")
        # Pipeline becomes: [validate_payment, validate, authorize, ...]
    """
    _insert_processor(intent_name, processor_name, position=0)


def after(intent_name: str, processor_name: str) -> None:
    """Add a processor AFTER the last processor in pipeline.

    Usage:
        after("process_payment", "send_receipt")
        # Pipeline becomes: [validate, authorize, ..., send_receipt]
    """
    config = _get_or_create_override(intent_name)
    _pipeline_overrides[intent_name] = PipelineConfig(
        processors=(*config.processors, processor_name),
        priority=config.priority,
        timeout=config.timeout,
        metadata=config.metadata,
    )


def before_processor(
    intent_name: str,
    target_processor: str,
    new_processor: str,
) -> None:
    """Add a processor BEFORE a specific processor.

    Usage:
        before_processor("process_payment", "authorize", "check_fraud")
        # Pipeline: [validate, check_fraud, authorize, ...]
    """
    config = _get_or_create_override(intent_name)
    processors = list(config.processors)

    if target_processor in processors:
        idx = processors.index(target_processor)
        processors.insert(idx, new_processor)
    else:
        processors.append(new_processor)

    _pipeline_overrides[intent_name] = PipelineConfig(
        processors=tuple(processors),
        priority=config.priority,
        timeout=config.timeout,
        metadata=config.metadata,
    )


def after_processor(
    intent_name: str,
    target_processor: str,
    new_processor: str,
) -> None:
    """Add a processor AFTER a specific processor.

    Usage:
        after_processor("process_payment", "validate", "enrich_data")
        # Pipeline: [validate, enrich_data, authorize, ...]
    """
    config = _get_or_create_override(intent_name)
    processors = list(config.processors)

    if target_processor in processors:
        idx = processors.index(target_processor)
        processors.insert(idx + 1, new_processor)
    else:
        processors.append(new_processor)

    _pipeline_overrides[intent_name] = PipelineConfig(
        processors=tuple(processors),
        priority=config.priority,
        timeout=config.timeout,
        metadata=config.metadata,
    )


def replace_pipeline(intent_name: str, processors: list[str]) -> None:
    """Replace entire pipeline for an intent.

    Usage:
        replace_pipeline("process_payment", ["custom_validate", "custom_pay"])
    """
    _pipeline_overrides[intent_name] = PipelineConfig(
        processors=tuple(processors),
    )


def remove_processor(intent_name: str, processor_name: str) -> None:
    """Remove a processor from pipeline.

    Usage:
        remove_processor("process_payment", "audit")
    """
    config = _get_or_create_override(intent_name)
    processors = tuple(p for p in config.processors if p != processor_name)

    _pipeline_overrides[intent_name] = PipelineConfig(
        processors=processors,
        priority=config.priority,
        timeout=config.timeout,
        metadata=config.metadata,
    )


# ============================================================
# 3. Get pipeline config (with overrides)
# ============================================================

def get_pipeline_config(intent: Intent) -> PipelineConfig:
    """Get pipeline config for an intent, including overrides.

    This is what the runtime calls to get the pipeline.
    """
    # Check for override first
    if intent.name in _pipeline_overrides:
        return _pipeline_overrides[intent.name]

    # Fall back to default resolution
    return resolve_pipeline(intent)


# ============================================================
# 4. Introspection
# ============================================================

def list_overrides() -> dict[str, list[str]]:
    """List all pipeline overrides."""
    return {
        name: list(config.processors)
        for name, config in _pipeline_overrides.items()
    }


def clear_overrides() -> None:
    """Clear all pipeline overrides."""
    _pipeline_overrides.clear()


# ============================================================
# Helpers
# ============================================================

def _get_or_create_override(intent_name: str) -> PipelineConfig:
    """Get existing override or create from default."""
    if intent_name in _pipeline_overrides:
        return _pipeline_overrides[intent_name]

    # Get level from registered intent
    from .intent import _registry
    intent = _registry.get(intent_name)
    level = intent.level if intent else Level.STANDARD

    # Create from level-appropriate default processors
    return PipelineConfig(
        processors=_DEFAULT_PROCESSORS.get(level, ("validate",)),
    )


def _insert_processor(
    intent_name: str,
    processor_name: str,
    position: int = 0,
) -> None:
    """Insert processor at position."""
    config = _get_or_create_override(intent_name)
    processors = list(config.processors)
    processors.insert(position, processor_name)

    _pipeline_overrides[intent_name] = PipelineConfig(
        processors=tuple(processors),
        priority=config.priority,
        timeout=config.timeout,
        metadata=config.metadata,
    )
