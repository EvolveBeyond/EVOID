# Custom Pipelines

Define your own pipeline for specific intents.

## Basic Usage

```python
from evoid import Intent, Level, add_intent_with_pipeline

MY_INTENT = Intent(name="process_payment", level=Level.CRITICAL)

async def handle_payment(ctx) -> dict:
    return {"status": "success"}

add_intent_with_pipeline(
    MY_INTENT,
    processors=["validate", "check_fraud", "pay", "notify"],
    handler=handle_payment,
)
```

## Replace Entire Pipeline

```python
from evoid import replace_pipeline

replace_pipeline("process_payment", ["custom_validate", "custom_pay"])
```

## See the Pipeline

```python
from evoid import list_overrides

overrides = list_overrides()
print(overrides)
# {"process_payment": ["validate", "check_fraud", "pay", "notify"]}
```
