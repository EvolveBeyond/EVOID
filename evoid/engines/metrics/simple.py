"""Simple Metrics Engine — Counters and timers.

IOP: Just dicts and functions. No class state.
"""

from __future__ import annotations

import time
from typing import Any


# Metrics storage
_counters: dict[str, int] = {}
_timers: dict[str, list[float]] = {}


def increment(name: str, value: int = 1) -> None:
    """Increment a counter."""
    _counters[name] = _counters.get(name, 0) + value


def gauge(name: str, value: float) -> None:
    """Set a gauge value."""
    _counters[name] = int(value)


def timer_start(name: str) -> float:
    """Start a timer, return start time."""
    return time.monotonic()


def timer_stop(name: str, start: float) -> None:
    """Stop a timer and record duration."""
    duration = time.monotonic() - start
    _timers.setdefault(name, []).append(duration)


def get_counter(name: str) -> int:
    """Get counter value."""
    return _counters.get(name, 0)


def get_timer_stats(name: str) -> dict[str, float]:
    """Get timer statistics."""
    durations = _timers.get(name, [])
    if not durations:
        return {"count": 0, "min": 0, "max": 0, "avg": 0}
    return {
        "count": len(durations),
        "min": min(durations),
        "max": max(durations),
        "avg": sum(durations) / len(durations),
    }


def all_metrics() -> dict[str, Any]:
    """Return all metrics."""
    return {
        "counters": _counters.copy(),
        "timers": {k: get_timer_stats(k) for k in _timers},
    }


def clear() -> None:
    """Clear all metrics."""
    _counters.clear()
    _timers.clear()
