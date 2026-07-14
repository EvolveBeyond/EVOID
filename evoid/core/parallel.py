"""Parallel — Async, multi-thread, and parallel execution.

IOP: Parallel execution is just function composition.
Users can:
1. Run intents in parallel (gather)
2. Run intents with priority ordering
3. Control concurrency limits
4. Use thread pools for CPU-bound work
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from .intent import Intent, Level
from .pipeline import Result
from .runtime import execute as execute_intent


# ============================================================
# Parallel execution
# ============================================================

# Thread pool for CPU-bound work
_thread_pool: ThreadPoolExecutor | None = None


def _get_thread_pool() -> ThreadPoolExecutor:
    """Get or create thread pool."""
    global _thread_pool
    if _thread_pool is None:
        _thread_pool = ThreadPoolExecutor(max_workers=4)
    return _thread_pool


async def gather(
    *intents: Intent,
    concurrency: int = 10,
    return_exceptions: bool = False,
) -> list[Result]:
    """Execute multiple intents in parallel.

    Usage:
        results = await gather(intent1, intent2, intent3)
        results = await gather(intent1, intent2, concurrency=5)
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_execute(intent: Intent) -> Result:
        async with semaphore:
            return await execute_intent(intent)

    tasks = [limited_execute(intent) for intent in intents]
    return await asyncio.gather(*tasks, return_exceptions=return_exceptions)


async def gather_with_priority(
    *intents: Intent,
    concurrency: int = 10,
) -> list[Result]:
    """Execute intents with priority ordering.

    Higher priority intents execute first.
    Uses priority queue for ordering.
    """
    # Sort by priority (higher first)
    sorted_intents = sorted(intents, key=lambda i: i.priority, reverse=True)

    semaphore = asyncio.Semaphore(concurrency)
    results: list[Result] = []

    async def limited_execute(intent: Intent) -> Result:
        async with semaphore:
            return await execute_intent(intent)

    # Execute in priority order
    tasks = [limited_execute(intent) for intent in sorted_intents]
    results = await asyncio.gather(*tasks)

    return results


async def parallel(
    *funcs: Callable[[], Awaitable[Any]],
    concurrency: int = 10,
) -> list[Any]:
    """Execute multiple async functions in parallel.

    Usage:
        results = await parallel(
            lambda: fetch_users(),
            lambda: fetch_orders(),
            lambda: fetch_products(),
        )
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_call(func: Callable) -> Any:
        async with semaphore:
            return await func()

    tasks = [limited_call(func) for func in funcs]
    return await asyncio.gather(*tasks)


def run_in_thread(
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Run a synchronous function in a thread pool.

    Use for CPU-bound work that would block the event loop.

    Usage:
        result = run_in_thread(cpu_intensive_function, arg1, arg2)
    """
    import functools
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(
        _get_thread_pool(),
        functools.partial(func, *args, **kwargs),
    )


async def run_in_thread_async(
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Run a synchronous function in a thread pool (async version).

    Usage:
        result = await run_in_thread_async(cpu_intensive_function, arg1)
    """
    import functools
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _get_thread_pool(),
        functools.partial(func, *args, **kwargs),
    )


# ============================================================
# Priority queue for intents
# ============================================================

@dataclass(order=True)
class PrioritizedIntent:
    """Intent with priority for queue ordering."""

    priority: int
    intent: Intent = field(compare=False)
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)


class IntentQueue:
    """Priority queue for intents.

    Intents are executed based on priority (higher first).
    """

    def __init__(self, max_concurrent: int = 10) -> None:
        self._queue: list[PrioritizedIntent] = []
        self._max_concurrent = max_concurrent
        self._running = 0
        self._semaphore = asyncio.Semaphore(max_concurrent)

    def enqueue(self, intent: Intent, priority: int = 0) -> None:
        """Add intent to queue."""
        item = PrioritizedIntent(priority=priority, intent=intent)
        self._queue.append(item)
        self._queue.sort(reverse=True)  # Higher priority first

    def dequeue(self) -> Intent | None:
        """Remove and return highest priority intent."""
        if self._queue:
            return self._queue.pop(0).intent
        return None

    async def process(self) -> list[Result]:
        """Process all intents in queue with priority ordering."""
        results = []

        async def process_one(intent: Intent) -> Result:
            async with self._semaphore:
                return await execute_intent(intent)

        while self._queue:
            intent = self.dequeue()
            if intent:
                result = await process_one(intent)
                results.append(result)

        return results

    @property
    def size(self) -> int:
        """Queue size."""
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0
