# Pipeline

A **Pipeline** is a sequence of processors executed in order.

## How it Works

```
Intent → Resolver → PipelineConfig → Execute Processors → Result
```

## Default Pipelines

| Level | Default Processors |
|-------|-------------------|
| EPHEMERAL | `validate` |
| STANDARD | `validate`, `authorize` |
| CRITICAL | `validate`, `authorize`, `audit`, `protect` |

## Custom Pipelines

```python
from evoid import add_intent_with_pipeline

add_intent_with_pipeline(
    Intent(name="payment", level=Level.CRITICAL),
    processors=["validate", "check_fraud", "pay", "send_receipt"],
)
```

## Extending Pipelines

```python
from evoid import before, after, before_processor, after_processor

# Add at beginning/end
before("payment", "log_start")
after("payment", "log_end")

# Add before/after specific processor
before_processor("payment", "authorize", "check_fraud")
after_processor("payment", "pay", "send_receipt")
```

## Replacing Pipelines

```python
from evoid import replace_pipeline

replace_pipeline("payment", ["custom_validate", "custom_pay"])
```

## Executing

```python
from evoid import execute

result = await execute(intent)
print(result.success)  # True/False
print(result.value)    # Result value
print(result.processors)  # Which processors ran
```
