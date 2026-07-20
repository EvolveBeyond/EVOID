---
title: 'Order API'
description: 'Complex orders — nested models, multiple parameters, query models.'
---

# Order API

Complex orders — nested models, multiple parameters, query models.

## Order with Multiple Items

```python
from pydantic import BaseModel, Field
from evoid.adapters.asgi import get, post
from evoid.web.route import Service

app = Service("sandy-api")

class OrderItem(BaseModel):
    sandwich: str
    quantity: int = Field(ge=1, le=100)
    special_instructions: str = ""

class CreateOrder(BaseModel):
    customer_name: str = Field(min_length=1)
    items: list[OrderItem] = Field(min_length=1)
    delivery_address: str | None = None

ORDERS = []

@post("/orders")
async def create_order(order: CreateOrder) -> dict:
    total = 0
    for item in order.items:
        price = MENU_PRICES.get(item.sandwich, 8.99)
        total += price * item.quantity

    new_order = {
        "id": len(ORDERS) + 1,
        "customer": order.customer_name,
        "items": [i.model_dump() for i in order.items],
        "total": total,
        "status": "confirmed",
        "delivery": order.delivery_address,
    }
    ORDERS.append(new_order)
    return {"status": "created", "order": new_order}
```

## What Happens Under the Hood

When you write `@post("/orders")` with a Pydantic model:

```python
@post("/orders")
async def create_order(order: CreateOrder) -> dict:
    ...
```

EVOID does this:

```python
# 1. Creates Intent
CREATE_ORDER = Intent(
    name="POST:/orders",
    level=Level.STANDARD,
    metadata={"method": "POST", "path": "/orders"},
)

# 2. Wraps your function — extracts body, validates with Pydantic
async def processor(ctx: Context) -> dict:
    body = ctx.metadata.get("body", {})
    order = CreateOrder(**body)  # Pydantic validates here
    return await create_order(order)

register_processor("POST:/orders", processor)
```

Your function receives a validated `CreateOrder` instance. EVOID handles extraction and validation.

## Query Parameter Models

For complex query strings, use a Pydantic model:

```python
from pydantic import BaseModel, Field

class OrderQuery(BaseModel):
    status: str | None = None
    min_total: float | None = None
    max_total: float | None = None
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)

@get("/orders")
async def list_orders(query: OrderQuery) -> dict:
    results = ORDERS

    if query.status:
        results = [o for o in results if o["status"] == query.status]
    if query.min_total:
        results = [o for o in results if o["total"] >= query.min_total]
    if query.max_total:
        results = [o for o in results if o["total"] <= query.max_total]

    # Pagination
    start = (query.page - 1) * query.limit
    end = start + query.limit

    return {
        "orders": results[start:end],
        "total": len(results),
        "page": query.page,
    }
```

```bash
curl "http://localhost:8000/orders?status=confirmed&min_total=20&page=1"
```

## Nested Response Models

Define structured responses:

```python
class OrderResponse(BaseModel):
    id: int
    customer: str
    items: list[OrderItem]
    total: float
    status: str

class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
    page: int

@get("/orders/{order_id}")
async def get_order(order_id: int) -> dict:
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if not order:
        return {"error": "Order not found"}
    return order
```

## Multiple Body Parameters

Pass multiple typed arguments — EVOID extracts them from the body:

```python
@post("/orders/quick")
async def quick_order(sandwich: str, qty: int = 1, name: str = "Guest") -> dict:
    price = MENU_PRICES.get(sandwich, 8.99)
    return {
        "customer": name,
        "sandwich": sandwich,
        "quantity": qty,
        "total": price * qty,
    }
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Nested models | Pydantic models inside other models |
| List fields | `list[OrderItem]` for arrays |
| Field constraints | `ge=1`, `le=100`, `min_length=1` |
| Query models | Complex query parameters as Pydantic |
| Pagination | Page + limit pattern |
| Response models | Structured, documented responses |

## Next: Validation

Let's add proper validation — [Validation](validation.md).
