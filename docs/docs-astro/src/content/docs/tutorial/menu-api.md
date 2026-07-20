---
title: 'Menu API'
description: 'Full CRUD for Sandy menu — path parameters, body updates, validation.'
---

# Menu API

Full CRUD for Sandy's menu — path parameters, body updates, validation.

## Complete Menu CRUD

```python
from evoid.adapters.asgi import get, post, put, delete
from evoid.web.route import Service

app = Service("sandy-api")

MENU = [
    {"id": 1, "name": "BLT", "price": 8.99, "category": "classic"},
    {"id": 2, "name": "Club", "price": 9.99, "category": "classic"},
    {"id": 3, "name": "Veggie", "price": 7.99, "category": "healthy"},
]

# List all items
@get("/menu")
async def list_menu() -> dict:
    return {"menu": MENU, "count": len(MENU)}

# Get one item — path parameter
@get("/menu/{item_id}")
async def get_item(item_id: int) -> dict:
    item = next((m for m in MENU if m["id"] == item_id), None)
    if not item:
        return {"error": "Item not found"}
    return item

# Add item — body parameters
@post("/menu")
async def add_item(name: str, price: float, category: str = "custom") -> dict:
    new_item = {
        "id": len(MENU) + 1,
        "name": name,
        "price": price,
        "category": category,
    }
    MENU.append(new_item)
    return {"status": "added", "item": new_item}

# Update item — path + body
@put("/menu/{item_id}")
async def update_item(item_id: int, name: str = None, price: float = None) -> dict:
    item = next((m for m in MENU if m["id"] == item_id), None)
    if not item:
        return {"error": "Item not found"}
    if name:
        item["name"] = name
    if price:
        item["price"] = price
    return {"status": "updated", "item": item}

# Delete item
@delete("/menu/{item_id}")
async def delete_item(item_id: int) -> dict:
    global MENU
    MENU = [m for m in MENU if m["id"] != item_id]
    return {"status": "deleted"}
```

## What Happens Under the Hood

Each `@get`, `@post`, `@put`, `@delete` decorator does three things:

```python
# @get("/menu/{item_id}") secretly creates:
GET_ITEM = Intent(
    name="GET:/menu/{item_id}",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/menu/{item_id}"},
)
register(GET_ITEM)

# Your handler is wrapped as a processor:
async def processor(ctx: Context) -> dict:
    params = ctx.metadata.get("params", {})
    return await get_item(**params)  # item_id extracted from URL

register_processor("GET:/menu/{item_id}", processor)
```

When `GET /menu/42` arrives:
1. EVOID matches the URL to Intent `GET:/menu/{item_id}`
2. Extracts `item_id=42` from the path
3. Calls your function with `get_item(item_id=42)`

You write plain functions. EVOID handles Intent creation, parameter extraction, and pipeline execution.

## Path Parameters

Extract dynamic values from the URL:

```python
@get("/menu/{item_id}")
async def get_item(item_id: int) -> dict:
    # item_id is automatically converted to int
    return {"id": item_id}

@get("/files/{path:path}")
async def get_file(path: str) -> dict:
    # path: supports slashes
    return {"path": path}

@get("/users/{user_id}/orders/{order_id}")
async def get_user_order(user_id: int, order_id: int) -> dict:
    # Multiple parameters
    return {"user": user_id, "order": order_id}
```

## Body Parameters

For POST/PUT requests, parameters come from the request body:

```python
@post("/menu")
async def add_item(name: str, price: float, category: str = "custom") -> dict:
    # name and price are required (no default)
    # category is optional (has default)
    return {"name": name, "price": price, "category": category}
```

## Query Parameters

Parameters with default values become optional query params:

```python
@get("/menu")
async def list_menu(category: str = None, max_price: float = None) -> dict:
    items = MENU
    if category:
        items = [m for m in items if m["category"] == category]
    if max_price:
        items = [m for m in items if m["price"] <= max_price]
    return {"menu": items}
```

```bash
curl "http://localhost:8000/menu?category=classic&max_price=10"
```

## Pydantic Models for Complex Bodies

For structured request bodies, use Pydantic models:

```python
from pydantic import BaseModel, Field

class MenuItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, lt=100)
    category: str = "custom"

@post("/menu")
async def add_item(item: MenuItem) -> dict:
    new_item = {"id": len(MENU) + 1, **item.model_dump()}
    MENU.append(new_item)
    return {"status": "added", "item": new_item}
```

This validates the entire body structure automatically.

## Partial Updates

For PUT requests that update only some fields:

```python
class MenuUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    category: str | None = None

@put("/menu/{item_id}")
async def update_item(item_id: int, updates: MenuUpdate) -> dict:
    item = next((m for m in MENU if m["id"] == item_id), None)
    if not item:
        return {"error": "Item not found"}

    # Only update fields that were provided
    update_data = updates.model_dump(exclude_unset=True)
    item.update(update_data)

    return {"status": "updated", "item": item}
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Path parameters | `{param}` in URL, typed extraction |
| Body parameters | Named args from POST/PUT body |
| Query parameters | Optional params with defaults |
| Pydantic models | Structured, validated request bodies |
| Partial updates | `model_dump(exclude_unset=True)` for PATCH-like behavior |

## Next: Order API

Now let's build the order system with complex bodies and nested models — [Order API](order-api.md).
