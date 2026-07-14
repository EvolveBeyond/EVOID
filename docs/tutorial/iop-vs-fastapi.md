# IOP vs @route

Both are IOP underneath. Just different syntax sugar.

## Side by Side 📊

### @route

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}

@app.post("/users")
async def create_user(name: str) -> dict:
    return {"status": "created"}
```

### IOP Style

```python
from evoid import Intent, Level, add_intent, create_service, on

app = create_service("my-api")

GET_USER = Intent(name="get_user", level=Level.STANDARD)
CREATE_USER = Intent(name="create_user", level=Level.STANDARD)

async def get_user(intent: Intent) -> dict:
    return {"id": intent.metadata.get("user_id")}

async def create_user(intent: Intent) -> dict:
    return {"status": "created"}

on(app, GET_USER, get_user)
on(app, CREATE_USER, create_user)
```

## What's the Same? ✅

| Feature | @route | IOP Style |
|---------|---------------|-----------|
| Intent created | ✅ Auto | ✅ Manual |
| Pipeline | ✅ Default | ✅ Custom |
| Processors | ✅ Built-in | ✅ Custom |
| Parallel execution | ✅ Yes | ✅ Yes |
| Inter-service communication | ✅ Yes | ✅ Yes |

## What's Different? 🔄

| Feature | @route | IOP Style |
|---------|---------------|-----------|
| Intent creation | Automatic | Manual |
| Syntax sugar | More | Less |
| Control | Less | More |
| Learning curve | Easier | Steeper |

## When to Use Which? 🤔

| Scenario | Recommended |
|----------|-------------|
| Quick prototype | @route ✅ |
| Small project | @route ✅ |
| Learning IOP | @route → IOP |
| Full control needed | IOP ✅ |
| Complex pipelines | IOP ✅ |
| Custom processors | IOP ✅ |

**Both are IOP. Just different sugar.** 🍬
