"""EVOID Core — IOP Runtime. Pure functions, pure data.

No classes with behavior. No inheritance. No stateful objects.
Just data carrying intent, and functions composing pipelines.
"""

from .intent import Intent, Level, register, resolve, all_intents, clear_registry
from .resolver import PipelineConfig, resolve_pipeline
from .pipeline import Result, execute as execute_pipeline
from .context import Context, fork
from .processor import Processor, register as register_processor, get as get_processor, all_processors
from .runtime import Config, execute, execute_by_name
from .message_bus import Message, subscribe, unsubscribe, publish, get_history
from .service import Service

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
]
