# Inter-Service Communication

Services communicate through Intents, not HTTP.

## Basic Usage

```python
from evoid.core import Intent, Level, Service
from evoid.core.service import start, stop, on, call, emit

# Create services
payment_service = Service(name="payment")
email_service = Service(name="email")

# Register handlers
async def handle_payment(intent: Intent) -> dict:
    return {"status": "success"}

on(payment_service, "process_payment", handle_payment)

# Start services
start(payment_service)
start(email_service)

# Call another service (no HTTP overhead)
result = await call(
    payment_service,
    Intent(name="process_payment", level=Level.CRITICAL, metadata={"amount": 99.99}),
)
print(result)  # {"status": "success"}

# Fire-and-forget
await emit(
    payment_service,
    Intent(name="send_email", level=Level.STANDARD, metadata={"to": "user@example.com"}),
)

# Stop services
stop(payment_service)
stop(email_service)
```

## Message Bus

```python
from evoid import subscribe, publish

# Subscribe to topic
async def handler(intent: Intent):
    print(f"Received: {intent.name}")

subscribe("payment.completed", handler)

# Publish
await publish(Intent(name="payment.completed", level=Level.STANDARD))
```
