---
title: 'Going Online'
description: 'Sandy gets a website. First @route endpoint, what happens under the hood.'
---

# Going Online

Sandy gets a website. First @route endpoint, what happens under the hood.

## The First Web Endpoint

```python
from evoid.adapters.asgi import get
from evoid.web.route import Service

app = Service("sandy-api")

@get("/menu")
async def list_menu() -> dict:
    return {"menu": [
        {"name": "BLT", "price": 8.99},
        {"name": "Club", "price": 9.99},
        {"name": "Veggie", "price": 7.99},
    ]}
```

That's it. One decorator, one function, one endpoint.

## What Happens Under the Hood

When you write `@get("/menu")`, EVOID does this:

```python
# 1. Creates an Intent
GET_MENU = Intent(
    name="GET:/menu",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/menu"},
)

# 2. Registers the Intent
register(GET_MENU)

# 3. Wraps your function as a processor
async def processor(ctx: Context) -> dict:
    return await list_menu()

# 4. Registers the processor
register_processor("GET:/menu", processor)
```

When a request arrives at `GET /menu`:
1. EVOID resolves the Intent `GET:/menu`
2. Builds the pipeline (default: `validate`, `authorize`)
3. Executes processors in order
4. Returns the result as JSON

## Running the Server

```python
from evoid.web.route import run

asyncio.run(run(app, host="0.0.0.0", port=8000))
```

Or via CLI:

```bash
evo service run sandy-api
```

## Testing It

```bash
curl http://localhost:8000/menu
# {"menu": [{"name": "BLT", "price": 8.99}, ...]}
```

## More Endpoints

```python
from evoid.adapters.asgi import get, post
from evoid.web.route import Service

app = Service("sandy-api")

@get("/menu")
async def list_menu() -> dict:
    return {"menu": MENU}

@get("/menu/{item_id}")
async def get_item(item_id: int) -> dict:
    item = next((m for m in MENU if m["id"] == item_id), None)
    if not item:
        return {"error": "Item not found"}
    return item

@post("/orders")
async def create_order(sandwich: str, qty: int = 1) -> dict:
    return {"status": "confirmed", "sandwich": sandwich, "qty": qty}
```

## What @route Gives You

| Feature | How |
|---------|-----|
| Path parameters | `{item_id}` in path, extracted as typed args |
| Body parameters | Named args extracted from POST body |
| Query parameters | Default values become optional query params |
| Auto-Intent creation | No manual `Intent()` needed |
| Pipeline integration | Handlers run through the default pipeline |

## @route vs Native IOP

| | @route | Native IOP |
|---|--------|------------|
| Syntax | `@get("/menu")` | `Intent(name="GET:/menu", ...)` |
| Intent | Auto-created | Explicitly created |
| Control | Less | Full |
| Best for | Web APIs | Any interface |

Both are IOP. @route is sugar that creates Intents for you. Under the hood, it's the same pipeline.

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `Service` | Named container for related endpoints |
| `@get` / `@post` | Decorators that auto-create Intents |
| Path parameters | `{param}` in URL, extracted as typed args |
| Auto-Intent | Decorator creates Intent from method + path |
| Pipeline | Handlers run through the default processor chain |

## Next: Menu API

Let's build the full CRUD for Sandy's menu — [Menu API](menu-api.md).
