# Path Parameters

Extract data from URL path.

## Basic Usage

```python
from evoid.web.route import Service, get

app = Service("my-api")

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}
```

Test it:

```bash
curl http://localhost:8000/users/123
# {"id": 123, "name": "User 123"}
```

## Type Conversion

```python
@app.get("/items/{item_id}")
async def get_item(item_id: int) -> dict:
    # item_id is automatically converted to int
    return {"id": item_id}
```

## Multiple Parameters

```python
@app.get("/users/{user_id}/orders/{order_id}")
async def get_user_order(user_id: int, order_id: int) -> dict:
    return {"user_id": user_id, "order_id": order_id}
```

## What Happens Behind the Scenes?

```
@app.get("/users/{user_id}")
        ↓
Intent(name="GET:/users/{user_id}", level=STANDARD)
        ↓
register(intent)
        ↓
register_processor(intent.name, handler)
```

The path `{user_id}` becomes part of the Intent name!
