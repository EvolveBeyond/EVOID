"""EVOID Core — IOP Runtime. Pure functions, pure data.

No classes with behavior. No inheritance. No stateful objects.
Just data carrying intent, and functions composing pipelines.
"""

from .context import Context, fork
from .intent import Intent, Level, all_intents, clear_registry, register, resolve
from .message_bus import Message, get_history, publish, subscribe, unsubscribe
from .pipeline import Result
from .pipeline import execute as execute_pipeline
from .processor import Processor, all_processors
from .processor import get as get_processor
from .processor import register as register_processor
from .resolver import PipelineConfig, resolve_pipeline
from .runtime import Config, execute, execute_by_name
from .service import Service

# Events
from .events import Event, EventContext, on as on_event, off as off_event, emit, emit_sync, hook_count

# Schema Export
from .schema import IntentSchema, FieldSchema, export_schemas, export_schema_for, export_json_schemas, export_json_schema

# Annotations
from .annotations import intent as intent_decorator, requires, validates, rate_limit, body, params, headers, apply_annotations, validate_annotations

# Convenience functions (Intent-based engine access)
from . import intents, storage, cache

__all__ = [
    # Intent
    "Intent",
    "Level",
    "register",
    "resolve",
    "all_intents",
    "clear_registry",
    # Resolver
    "PipelineConfig",
    "resolve_pipeline",
    # Pipeline
    "Result",
    "execute_pipeline",
    # Context
    "Context",
    "fork",
    # Processor
    "Processor",
    "register_processor",
    "get_processor",
    "all_processors",
    # Runtime
    "Config",
    "execute",
    "execute_by_name",
    # Message Bus
    "Message",
    "subscribe",
    "unsubscribe",
    "publish",
    "get_history",
    # Service
    "Service",
    # Events
    "Event",
    "EventContext",
    "on_event",
    "off_event",
    "emit",
    "emit_sync",
    "hook_count",
    # Schema Export
    "IntentSchema",
    "FieldSchema",
    "export_schemas",
    "export_schema_for",
    "export_json_schemas",
    "export_json_schema",
    # Annotations
    "intent_decorator",
    "requires",
    "validates",
    "rate_limit",
    "body",
    "params",
    "headers",
    "apply_annotations",
    "validate_annotations",
]
