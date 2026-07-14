# Concurrency and Async in EVOID

Details about how EVOID handles concurrency, async/await, and parallel execution.

## In a hurry?

**TL;DR:**

EVOID is fully async-native. You can:

- ✅ Run multiple intents in parallel
- ✅ Control concurrency limits
- ✅ Use priority-based execution
- ✅ Run CPU-bound work in threads

```python
from evoid import gather, Intent, Level

# Run 3 intents in parallel
intent1 = Intent(name="fetch_users", level=Level.STANDARD)
intent2 = Intent(name="fetch_orders", level=Level.STANDARD)
intent3 = Intent(name="fetch_products", level=Level.STANDARD)

results = await gather(intent1, intent2, intent3)
# All 3 execute simultaneously! 🚀
```

---

## Why Async Matters 🤔

### The Waiting Problem ⏰

Imagine you're running a web server. Every request involves:

1. Receiving data from client 📥
2. Processing data ⚙️
3. Sending response back 📤

Most of the time is spent **waiting** ⏰:

- Waiting for client to send data
- Waiting for database to respond
- Waiting for external API
- Waiting to send response

This "waiting" is called **I/O bound** operations.

### Sequential vs Concurrent 📊

**Sequential (Traditional):**
```
Request 1: ████████░░░░░░░░░░░░ (80% waiting, 20% work)
Request 2: ░░░░░░░░████████░░░░ (starts after Request 1 finishes)
Request 3: ░░░░░░░░░░░░░░░░████ (starts after Request 2 finishes)

Total: ████████████████████████████████ (very slow)
```

**Concurrent (EVOID):**
```
Request 1: ████████░░░░░░░░░░░░ (80% waiting)
Request 2: ░░████████░░░░░░░░░░ (starts while Request 1 waits)
Request 3: ░░░░░░░░████████░░░░ (starts while others wait)

Total: ████████████ (3x faster!)
```

**That's the power of async!** 🚀

---

## How EVOID Handles It ⚙️

### Automatic Async 🔄

When you use decorators, EVOID automatically handles async:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    # This runs asynchronously
    result = await fetch_from_database(user_id)
    return result
```

The `async def` tells Python this function might wait for I/O.

### Parallel Execution 🏃‍♂️

Run multiple intents at the same time:

```python
from evoid import gather

# These 3 intents run in parallel
results = await gather(intent1, intent2, intent3)

# With concurrency limit
results = await gather(intent1, intent2, intent3, concurrency=5)
```

### Priority-Based Execution 🎯

Run high-priority intents first:

```python
from evoid import gather_with_priority

# Products (priority=3) runs first
# Orders (priority=2) runs second
# Users (priority=1) runs last
results = await gather_with_priority(intent1, intent2, intent3)
```

### Thread Pool for CPU Work 🧮

For CPU-bound operations that would block the event loop:

```python
from evoid import run_in_thread_async

# Run in thread pool (doesn't block event loop)
result = await run_in_thread_async(cpu_intensive_function, arg1, arg2)
```

---

## The Intent Queue 📋

For complex workflows with priorities:

```python
from evoid import IntentQueue

queue = IntentQueue(max_concurrent=3)

# Add intents with priorities
queue.enqueue(intent_critical, priority=10)
queue.enqueue(intent_important, priority=5)
queue.enqueue(intent_normal, priority=1)

# Process in priority order
results = await queue.process()
```

---

## Real-World Example 🌍

```python
from evoid import gather, Intent, Level

# Fetch data from multiple sources simultaneously
users_intent = Intent(name="fetch_users", level=Level.STANDARD)
orders_intent = Intent(name="fetch_orders", level=Level.STANDARD)
products_intent = Intent(name="fetch_products", level=Level.STANDARD)

# All 3 fetch operations run in parallel
results = await gather(
    users_intent,
    orders_intent,
    products_intent,
    concurrency=10,
)

# Process results
users, orders, products = results
```

**Without parallel:** 300ms (100ms × 3)
**With parallel:** 100ms (max of 3)

**That's 3x faster!** 🚀

---

## Conclusion ✨

EVOID's async capabilities:

- 🔄 **Automatic:** Decorators handle async for you
- 🏃‍♂️ **Parallel:** Run multiple intents simultaneously
- 🎯 **Priority:** Execute important intents first
- 🧮 **Thread Pool:** Handle CPU-bound work efficiently
- 📋 **Queue:** Manage complex workflows

**IOP + Async = Maximum Performance** 🚀
