# Quick Start

## Create a new project

```bash
evo init my-api
cd my-api
```

This creates:
```
my-api/
├── evoid.toml      # Project config
├── services/       # Services directory
└── shared/         # Shared code
```

## Add a service

```bash
evo service new api
```

This creates:
```
services/api/
├── evoid.toml      # Service config
└── main.py         # Service code
```

## Run the service

```bash
evo service run api
```

Visit http://localhost:8000/health

## Edit the service

Open `services/api/main.py`:

```python
from evoid.web.route import Service, get, post, run
from evoid.engines.logger import loguru as log

app = Service("api")

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@app.post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "user": {"name": name, "email": email}}

if __name__ == "__main__":
    log.init("api")
    import asyncio
    asyncio.run(run(app, port=8000))
```

## Test it

```bash
curl http://localhost:8000/users/123
# {"id": 123, "name": "User 123"}

curl -X POST http://localhost:8000/users -d "name=Ali&email=ali@example.com"
# {"status": "created", "user": {"name": "Ali", "email": "ali@example.com"}}
```
