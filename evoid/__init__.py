"""EVOID — Reference Runtime for Intent-Oriented Programming.

IOP: Data carries its own intent.
     Processors are independent Lego blocks.
     Pipeline routes by purpose.
     Services communicate through Intents, not HTTP.
"""

__version__ = "0.3.3"

# Core
from .core import (
    Config,
    Context,
    Intent,
    Level,
    # Message Bus
    Message,
    PipelineConfig,
    Processor,
    Result,
    # Service
    Service,
    all_intents,
    all_processors,
    clear_registry,
    execute,
    execute_by_name,
    execute_pipeline,
    fork,
    get_history,
    get_processor,
    publish,
    register,
    register_processor,
    resolve,
    resolve_pipeline,
    subscribe,
    unsubscribe,
)

# Extend
from .core.extend import (
    add_intent,
    add_intent_with_pipeline,
    after,
    after_processor,
    before,
    before_processor,
    clear_overrides,
    get_pipeline_config,
    list_overrides,
    remove_processor,
    replace_pipeline,
)

# Parallel
from .core.parallel import (
    IntentQueue,
    gather,
    gather_with_priority,
    parallel,
    run_in_thread,
    run_in_thread_async,
)

# Native (IOP mother syntax)
from .native import (
    Service as NativeService,
)
from .native import (
    create_service,
    execute_service,
)
from .native import (
    on as native_on,
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
    # Native
    "NativeService",
    "create_service",
    "native_on",
    "execute_service",
]
