# Extending Pipelines

Add processors before/after existing ones.

## Before/After Route

```python
from evoid import before, after

# Add at beginning
before("GET:/users/{id}", "log_request")

# Add at end
after("GET:/users/{id}", "log_response")
```

## Before/After Specific Processor

```python
from evoid import before_processor, after_processor

# Add before authorize
before_processor("process_payment", "authorize", "check_fraud")

# Add after pay
after_processor("process_payment", "pay", "send_receipt")
```

## Replace Entire Pipeline

```python
from evoid import replace_pipeline

replace_pipeline("process_payment", ["validate", "pay", "notify"])
```

## Remove Processor

```python
from evoid import remove_processor

remove_processor("process_payment", "audit")
```

## List Overrides

```python
from evoid import list_overrides

overrides = list_overrides()
# {"process_payment": ["validate", "check_fraud", "authorize", "pay"]}
```

## Clear Overrides

```python
from evoid import clear_overrides

clear_overrides()
```
