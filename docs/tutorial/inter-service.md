# Inter-Service Communication

Services communicate through Intents, not HTTP.

## Basic Usage

```python
from evoid.core import Intent, Level, Service
from evoid.core.service import start, call

# Create services
payment_service = Service(name="payment")
email_service = Service(name="email")

# Register handlers
async def handle_payment(intent: Intent) -> dict:
    return {"status": "success"}

start(payment_service)

# Call another service
result = await call(
    payment_service,
    Intent(name="process_payment", level=Level.CRITICAL, metadata={"amount": 99.99}),
)
print(result)  # {"status": "success"}
```

## Fire and Forget

```python
from evoid.core.service import emit

# Send without waiting for response
await emit(
    email_service,
    Intent(name="send_email", level=Level.STANDARD, metadata={"to": "user@example.com"}),
)
```

## Why Intent-Based Communication? 🤔

- ✅ **No HTTP overhead** — Direct function calls
- ✅ **Type safe** — Intent defines the contract
- ✅ **Priority aware** — Important requests first
- ✅ **Resilient** — Circuit breaker built-in

**Intent-based communication is faster and safer.** 🚀
