# Building a REST API

Complete CRUD operations with EVOID.

## User API Example

```python
from evoid.web.route import Service, get, post, put, delete

app = Service("user-api")

# In-memory storage (for demo)
users = {}

@app.get("/users")
async def list_users() -> dict:
    return {"users": list(users.values())}

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    if user_id not in users:
        return {"error": "User not found"}
    return users[user_id]

@app.post("/users")
async def create_user(name: str, email: str) -> dict:
    user_id = len(users) + 1
    users[user_id] = {"id": user_id, "name": name, "email": email}
    return {"status": "created", "user": users[user_id]}

@app.put("/users/{user_id}")
async def update_user(user_id: int, name: str = None) -> dict:
    if user_id not in users:
        return {"error": "User not found"}
    if name:
        users[user_id]["name"] = name
    return {"status": "updated", "user": users[user_id]}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int) -> dict:
    if user_id not in users:
        return {"error": "User not found"}
    del users[user_id]
    return {"status": "deleted"}

if __name__ == "__main__":
    import asyncio
    from evoid.web.route import run
    asyncio.run(run(app, port=8000))
```

## Test It

```bash
# Create user
curl -X POST http://localhost:8000/users -d "name=Ali&email=ali@example.com"

# List users
curl http://localhost:8000/users

# Get user
curl http://localhost:8000/users/1

# Update user
curl -X PUT http://localhost:8000/users/1 -d "name=Sara"

# Delete user
curl -X DELETE http://localhost:8000/users/1
```

## What's Next?

Now let's add [authentication](authentication.md) to secure your API.
