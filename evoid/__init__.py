"""EVOID — Reference Runtime for Intent-Oriented Programming.

IOP: Data carries its own intent.
     Processors are independent Lego blocks.
     Pipeline routes by purpose.
     Services communicate through Intents, not HTTP.
"""

__version__ = "2.0.0-alpha"

# Core
from .core import (
    Intent,
    Level,
    register,
    resolve,
    all_intents,
    clear_registry,
    PipelineConfig,
    resolve_pipeline,
    Result,
    execute_pipeline,
    Context,
    fork,
    Processor,
    register_processor,
    get_processor,
    all_processors,
    Config,
    execute,
    execute_by_name,
    # Message Bus
    Message,
    subscribe,
    unsubscribe,
    publish,
    get_history,
    # Service
    Service,
)

# Extend
from .core.extend import (
    add_intent,
    add_intent_with_pipeline,
    before,
    after,
    before_processor,
    after_processor,
    replace_pipeline,
    remove_processor,
    get_pipeline_config,
    list_overrides,
    clear_overrides,
)

# Parallel
from .core.parallel import (
    gather,
    gather_with_priority,
    parallel,
    run_in_thread,
    run_in_thread_async,
    IntentQueue,
)

__all__ = [
    # Core
    "Intent",
    "Level",
    "register",
    "resolve",
    "all_intents",
    "clear_registry",
    "PipelineConfig",
    "resolve_pipeline",
    "Result",
    "execute_pipeline",
    "Context",
    "fork",
    "Processor",
    "register_processor",
    "get_processor",
    "all_processors",
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
    # Extend
    "add_intent",
    "add_intent_with_pipeline",
    "before",
    "after",
    "before_processor",
    "after_processor",
    "replace_pipeline",
    "remove_processor",
    "get_pipeline_config",
    "list_overrides",
    "clear_overrides",
    # Parallel
    "gather",
    "gather_with_priority",
    "parallel",
    "run_in_thread",
    "run_in_thread_async",
    "IntentQueue",
]
