# Extending Pipelines

Add processors before or after existing ones.

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

## See the Result

```python
from evoid import list_overrides

# Before extending
print(list_overrides())
# {}

# After extending
before("process_payment", "log_start")
after("process_payment", "log_end")

print(list_overrides())
# {"process_payment": ["log_start", "validate", "authorize", "log_end"]}
```

## Why Extend? 🤔

- ✅ Add logging without modifying existing code
- ✅ Add validation without changing handlers
- ✅ Add monitoring without touching business logic
- ✅ Keep code clean and maintainable

**Extend without modifying. That's the IOP way.** 🎯
