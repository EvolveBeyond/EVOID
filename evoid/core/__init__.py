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
