# The Pipeline

How Intent flows through the system.

## The Flow 🔄

```
Intent → Resolver → Pipeline → Processors → Result
```

## Step by Step

### 1. Intent Arrives 📥

```python
intent = Intent(name="GET:/users/123", level=Level.STANDARD)
```

### 2. Resolver Maps to Pipeline 🗺️

The resolver looks at the intent level and configures the pipeline:

```python
# Default pipelines
Level.EPHEMERAL → ["validate"]
Level.STANDARD  → ["validate", "authorize"]
Level.CRITICAL  → ["validate", "authorize", "audit", "protect"]
```

### 3. Pipeline Executes 🚀

```python
# For STANDARD intent
pipeline = ["validate", "authorize"]

# Execute each processor in order
for processor in pipeline:
    result = await processor(context)
```

### 4. Result Returns 📤

```python
result = Result(
    success=True,
    value={"id": 123, "name": "Ali"},
    processors=("validate", "authorize"),
    duration=0.001,
)
```

## Visual 📊

```
┌─────────────┐
│   Intent    │
│ "GET:/users"│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Resolver  │
│ STANDARD →  │
│ ["validate",│
│ "authorize"]│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Pipeline   │
│ ┌─────────┐ │
│ │validate │ │
│ └────┬────┘ │
│      ▼      │
│ ┌─────────┐ │
│ │authorize│ │
│ └────┬────┘ │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Result    │
│ {success:   │
│  True}      │
└─────────────┘
```
