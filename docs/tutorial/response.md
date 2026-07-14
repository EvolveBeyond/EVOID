# Response

Return data from your endpoints.

## Basic Usage

```python
from evoid.web.route import Service, get

app = Service("my-api")

@app.get("/hello")
async def hello() -> dict:
    return {"message": "Hello, EVOID!"}
```

## Return Different Types

```python
@app.get("/user")
async def get_user() -> dict:
    return {"id": 1, "name": "Ali"}

@app.get("/status")
async def get_status() -> str:
    return "ok"

@app.get("/count")
async def get_count() -> int:
    return 42
```

## Response with Status Code

```python
from fastapi.responses import JSONResponse

@app.post("/users")
async def create_user(name: str) -> JSONResponse:
    return JSONResponse(
        content={"status": "created", "name": name},
        status_code=201,
    )
```

## What Happens Behind the Scenes?

The handler returns a result. EVOID automatically:

1. Serializes the result to JSON
2. Sets the response headers
3. Returns the response to the client

**You just return data. EVOID handles the rest.** 🎯
