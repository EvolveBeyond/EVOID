# Request Body

Receive data from the request body.

## Basic Usage

```python
from evoid.web.route import Service, post

app = Service("my-api")

@app.post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "user": {"name": name, "email": email}}
```

Test it:

```bash
curl -X POST http://localhost:8000/users -d "name=Ali&email=ali@example.com"
# {"status": "created", "user": {"name": "Ali", "email": "ali@example.com"}}
```

## Using Pydantic Models

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    age: int = 0

@app.post("/users")
async def create_user(user: UserCreate) -> dict:
    return {"status": "created", "user": user.model_dump()}
```

## What Happens Behind the Scenes?

The request body is stored in Intent metadata:

```
Intent metadata = {
    "method": "POST",
    "path": "/users",
    "body": {"name": "Ali", "email": "ali@example.com"}
}
```

The processor can access this via `ctx.intent.metadata["body"]`.
