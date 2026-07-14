# Parallel Execution

Run multiple intents at the same time.

## Basic Usage

```python
from evoid import gather, Intent, Level

intent1 = Intent(name="fetch_users", level=Level.STANDARD)
intent2 = Intent(name="fetch_orders", level=Level.STANDARD)
intent3 = Intent(name="fetch_products", level=Level.STANDARD)

# Execute in parallel
results = await gather(intent1, intent2, intent3)
```

## With Concurrency Limit

```python
# Maximum 5 concurrent executions
results = await gather(intent1, intent2, intent3, concurrency=5)
```

## Priority Execution

```python
from evoid import gather_with_priority

# Higher priority executes first
results = await gather_with_priority(intent1, intent2, intent3)
```

## Intent Queue

```python
from evoid import IntentQueue

queue = IntentQueue(max_concurrent=3)

queue.enqueue(intent1, priority=1)
queue.enqueue(intent2, priority=2)
queue.enqueue(intent3, priority=3)

results = await queue.process()
```

## Speed Comparison 🚀

```
Sequential: 300ms (100ms × 3)
Parallel:   100ms (max of 3)

That's 3x faster! 🚀
```
