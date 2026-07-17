"""Processors — Built-in pipeline processors.

IOP: Processors are pure functions, not classes.
Each processor takes a Context and returns a result.

Available processors:
- intent_extractor: Extracts intent info from context
- schema_validator: Validates data against schema
- auth_checker: Checks authorization
- rate_limiter: Limits request rate
- circuit_breaker: Prevents cascading failures
- logger_processor: Logs pipeline execution
"""

from .auth_checker import process as auth_checker
from .circuit_breaker import process as circuit_breaker
from .intent_extractor import process as intent_extractor
from .logger_processor import process as logger_processor
from .rate_limiter import process as rate_limiter
from .schema_validator import process as schema_validator

__all__ = [
    "intent_extractor",
    "schema_validator",
    "auth_checker",
    "rate_limiter",
    "circuit_breaker",
    "logger_processor",
]
