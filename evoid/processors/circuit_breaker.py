"""Circuit Breaker — Prevents cascading failures.

IOP: Pure function. Simple state machine.
"""

from __future__ import annotations

import time
from typing import Any

from ..core.context import Context


# Circuit breaker state: service_name -> (state, failure_count, last_failure)
_states: dict[str, tuple[str, int, float]] = {}

# Default thresholds
_FAILURE_THRESHOLD = 3
_RECOVERY_TIMEOUT = 30.0  # seconds


async def process(ctx: Context) -> dict:
    """Check circuit breaker state before executing.

    If circuit is OPEN, reject the request.
    If circuit is HALF_OPEN, allow one request to test.
    """
    # Get service name from intent
    service = ctx.intent.metadata.get("service") or ctx.intent.name

    # Get current state
    state, failures, last_failure = _states.get(service, ("closed", 0, 0))

    now = time.time()

    if state == "open":
        # Check if recovery timeout has passed
        if now - last_failure >= _RECOVERY_TIMEOUT:
            # Transition to half-open
            _states[service] = ("half_open", failures, last_failure)
            return {"allowed": True, "state": "half_open"}
        else:
            # Still open, reject
            return {"allowed": False, "state": "open"}

    if state == "half_open":
        # Allow one request, will be reset on success
        return {"allowed": True, "state": "half_open"}

    # State is closed, allow
    return {"allowed": True, "state": "closed"}


def record_success(service: str) -> None:
    """Record a success — reset circuit breaker."""
    _states[service] = ("closed", 0, 0)


def record_failure(service: str) -> None:
    """Record a failure — increment count."""
    state, failures, last_failure = _states.get(service, ("closed", 0, 0))
    failures += 1

    if failures >= _FAILURE_THRESHOLD:
        _states[service] = ("open", failures, time.time())
    else:
        _states[service] = (state, failures, last_failure)


def get_state(service: str) -> dict[str, Any]:
    """Get circuit breaker state for a service."""
    state, failures, last_failure = _states.get(service, ("closed", 0, 0))
    return {
        "state": state,
        "failures": failures,
        "last_failure": last_failure,
    }
