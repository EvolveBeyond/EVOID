"""Parallel Execution Example — Async, multi-thread, priority.

This example shows how to:
1. Execute multiple intents in parallel
2. Use priority ordering
3. Control concurrency
4. Run CPU-bound work in threads
"""

import asyncio
import time

from evoid.core import Intent, Level, Context, register, register_processor
from evoid.core.parallel import (
    gather,
    gather_with_priority,
    parallel,
    run_in_thread_async,
    IntentQueue,
)
from evoid.engines.logger import loguru as log


# ============================================================
# 1. Define Intents
# ============================================================

FETCH_USERS = Intent(name="fetch_users", level=Level.STANDARD, priority=1)
FETCH_ORDERS = Intent(name="fetch_orders", level=Level.STANDARD, priority=2)
FETCH_PRODUCTS = Intent(name="fetch_products", level=Level.STANDARD, priority=3)
CPU_WORK = Intent(name="cpu_work", level=Level.CRITICAL, priority=10)


# ============================================================
# 2. Define Handlers
# ============================================================

async def handle_fetch_users(ctx: Context) -> dict:
    """Simulate fetching users (I/O bound)."""
    await asyncio.sleep(0.1)  # Simulate network delay
    return {"users": ["Ali", "Sara", "Mohammad"]}

async def handle_fetch_orders(ctx: Context) -> dict:
    """Simulate fetching orders (I/O bound)."""
    await asyncio.sleep(0.1)
    return {"orders": [{"id": 1, "total": 99.99}]}

async def handle_fetch_products(ctx: Context) -> dict:
    """Simulate fetching products (I/O bound)."""
    await asyncio.sleep(0.1)
    return {"products": [{"id": 1, "name": "Laptop"}]}

async def handle_cpu_work(ctx: Context) -> dict:
    """CPU-bound work."""
    # Simulate CPU work
    total = sum(i * i for i in range(100000))
    return {"result": total}


# Register with custom pipelines
from evoid.core.extend import add_intent_with_pipeline

add_intent_with_pipeline(FETCH_USERS, processors=["fetch_users"], handler=handle_fetch_users)
add_intent_with_pipeline(FETCH_ORDERS, processors=["fetch_orders"], handler=handle_fetch_orders)
add_intent_with_pipeline(FETCH_PRODUCTS, processors=["fetch_products"], handler=handle_fetch_products)
add_intent_with_pipeline(CPU_WORK, processors=["cpu_work"], handler=handle_cpu_work)


# ============================================================
# 3. Demo
# ============================================================

async def main():
    print("=" * 60)
    print("  EVOID Parallel Execution Demo")
    print("=" * 60)

    log.init("evoid-parallel", level="INFO")

    # 1. Sequential execution
    print("\n1. Sequential execution:")
    print("-" * 40)
    start = time.time()
    from evoid.core import execute
    await execute(FETCH_USERS)
    await execute(FETCH_ORDERS)
    await execute(FETCH_PRODUCTS)
    seq_time = time.time() - start
    print(f"   Time: {seq_time:.3f}s")

    # 2. Parallel execution (gather)
    print("\n2. Parallel execution (gather):")
    print("-" * 40)
    start = time.time()
    results = await gather(FETCH_USERS, FETCH_ORDERS, FETCH_PRODUCTS)
    par_time = time.time() - start
    print(f"   Time: {par_time:.3f}s")
    print(f"   Speedup: {seq_time/par_time:.1f}x")
    for r in results:
        print(f"   - {r.value}")

    # 3. Priority execution
    print("\n3. Priority execution:")
    print("-" * 40)
    start = time.time()
    results = await gather_with_priority(FETCH_USERS, FETCH_ORDERS, FETCH_PRODUCTS)
    pri_time = time.time() - start
    print(f"   Time: {pri_time:.3f}s")
    for r in results:
        print(f"   - {r.value}")

    # 4. Concurrency control
    print("\n4. Concurrency control (max 2):")
    print("-" * 40)
    start = time.time()
    results = await gather(FETCH_USERS, FETCH_ORDERS, FETCH_PRODUCTS, concurrency=2)
    con_time = time.time() - start
    print(f"   Time: {con_time:.3f}s (limited concurrency)")

    # 5. Thread pool for CPU work
    print("\n5. Thread pool (CPU-bound):")
    print("-" * 40)
    start = time.time()
    result = await run_in_thread_async(lambda: sum(i * i for i in range(100000)))
    thread_time = time.time() - start
    print(f"   Result: {result}")
    print(f"   Time: {thread_time:.3f}s")

    # 6. Intent Queue with priorities
    print("\n6. Intent Queue:")
    print("-" * 40)
    queue = IntentQueue(max_concurrent=2)
    queue.enqueue(FETCH_USERS, priority=1)
    queue.enqueue(FETCH_ORDERS, priority=2)
    queue.enqueue(FETCH_PRODUCTS, priority=3)

    print(f"   Queue size: {queue.size}")
    results = await queue.process()
    print(f"   Processed: {len(results)} intents")

    print("\n" + "=" * 60)
    print("  Done!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
