# API Reference

## Core

### Intent

```python
from evoid import Intent, Level

intent = Intent(
    name="my_intent",           # Unique name
    level=Level.STANDARD,       # EPHEMERAL, STANDARD, CRITICAL
    metadata={},                # Arbitrary data
    timeout=10.0,               # Max execution time (seconds)
    priority=0,                 # Execution priority (higher = first)
)
```

### execute

```python
from evoid import execute

result = await execute(intent)
# Result(success=True, value={...}, processors=('validate',), duration=0.001)
```

### register

```python
from evoid import register, Intent, Level

register(Intent(name="my_intent", level=Level.STANDARD))
```

### register_processor

```python
from evoid import register_processor

async def my_processor(ctx):
    return {"processed": True}

register_processor("my_processor", my_processor)
```

## Extend

### add_intent

```python
from evoid import add_intent

add_intent(intent, handler)
```

### add_intent_with_pipeline

```python
from evoid import add_intent_with_pipeline

add_intent_with_pipeline(intent, processors=["a", "b"], handler=fn)
```

### before / after

```python
from evoid import before, after

before("route", "processor")
after("route", "processor")
```

### before_processor / after_processor

```python
from evoid import before_processor, after_processor

before_processor("route", "target", "new_processor")
after_processor("route", "target", "new_processor")
```

## Parallel

### gather

```python
from evoid import gather

results = await gather(intent1, intent2, concurrency=5)
```

### gather_with_priority

```python
from evoid import gather_with_priority

results = await gather_with_priority(intent1, intent2)
```

### IntentQueue

```python
from evoid import IntentQueue

queue = IntentQueue(max_concurrent=3)
queue.enqueue(intent, priority=1)
results = await queue.process()
```

## Service

### Service

```python
from evoid import Service

service = Service(name="my-service")
```

### call / emit

```python
from evoid.core.service import call, emit

result = await call(service, intent)
await emit(service, intent)
```
