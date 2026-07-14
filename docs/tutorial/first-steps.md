# First Steps

Let's create your first EVOID service.

## Create a Service

Create a file `main.py`:

```python
from evoid.web.route import Service, get, run

app = Service("hello")

@app.get("/hello")
async def hello() -> dict:
    return {"message": "Hello, EVOID!"}

if __name__ == "__main__":
    import asyncio
    asyncio.run(run(app))
```

## Run It

```bash
python main.py
```

You'll see:

```
Starting hello on http://0.0.0.0:8000
```

## Test It

Open another terminal:

```bash
curl http://localhost:8000/hello
```

Response:

```json
{"message": "Hello, EVOID!"}
```

## What Happened?

1. `Service("hello")` — Creates an app (like FastAPI)
2. `@get("/hello")` — Registers a GET endpoint
3. **Behind the scenes**: An Intent is auto-created
4. `run(app)` — Starts the ASGI server

## Add More Endpoints

```python
from evoid.web.route import Service, get, post, run

app = Service("hello")

@app.get("/hello")
async def hello() -> dict:
    return {"message": "Hello, EVOID!"}

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@app.post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "user": {"name": name, "email": email}}

if __name__ == "__main__":
    import asyncio
    asyncio.run(run(app))
```

## Test the New Endpoints

```bash
# Get user
curl http://localhost:8000/users/123
# {"id": 123, "name": "User 123"}

# Create user
curl -X POST http://localhost:8000/users -d "name=Ali&email=ali@example.com"
# {"status": "created", "user": {"name": "Ali", "email": "ali@example.com"}}
```

## What's Next?

Now that you have a running service, let's understand [Intents](intents.md) — the core concept of EVOID.
