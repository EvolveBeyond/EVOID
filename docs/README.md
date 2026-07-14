# EVOID

**Reference Runtime for Intent-Oriented Programming**

EVOID is not a framework. It's a runtime specification for Intent-Oriented Programming (IOP).

## What is IOP?

Intent-Oriented Programming is a paradigm where developers declare **WHAT they want**, and the runtime decides **HOW to achieve it**.

```python
# Traditional: You tell the system HOW
def save_user(user):
    encrypted = encrypt(user.email)
    cache.set(f"user:{user.id}", encrypted, ttl=300)
    db.insert("users", encrypted)
    audit_log("user_created", user)

# IOP: You tell the system WHAT
class User(BaseModel):
    name: standard(str)      # Normal processing
    email: critical(str)     # Auto-encrypt, audit, replicate
    session: ephemeral(str)  # Memory only, auto-expire
```

## Quick Start

```bash
# Install
uv add evoid

# Create project
evo init my-api
cd my-api

# Add service
evo service new api

# Run
evo service run api
```

## Three Syntax Styles

### @route
```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}
```

### @controller
```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{id}")
    async def get_user(self, id: int) -> dict:
        return {"id": id}
```

### IOP Native
```python
from evoid import Intent, Level, add_intent

MY_INTENT = Intent(name="my_intent", level=Level.CRITICAL)

async def handle(intent: Intent) -> dict:
    return {"status": "ok"}

add_intent(MY_INTENT, handle)
```

All three styles are IOP underneath — just different syntax sugar.

## Links

- [GitHub](https://github.com/your-username/evoid)
- [PyPI](https://pypi.org/project/evoid/)
