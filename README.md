# EVOID

**Reference Runtime for Intent-Oriented Programming (IOP)**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-orange.svg)](https://github.com/EVOID/EVOID)
[![IOP](https://img.shields.io/badge/paradigm-IOP-purple.svg)](https://github.com/EVOID/EVOID)

---

## What is EVOID?

**EVOID is a runtime, not a framework.**

It's the reference implementation for **Intent-Oriented Programming (IOP)** — a new paradigm where your data model IS your infrastructure policy.

> 🧠 **Intent is permanent. Infrastructure is temporary.**

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

---

## Current Focus: Web Development 🌐

**EVOID is a full IOP runtime**, but right now we're focused on **web development capabilities**:

| Feature | Status | Description |
|---------|--------|-------------|
| ASGI Server | ✅ Ready | Production-grade ASGI adapter |
| @route Syntax | ✅ Ready | Familiar decorator style |
| @controller Syntax | ✅ Ready | Class-based for large projects |
| IOP Native | ✅ Ready | Full control over everything |
| Parallel Execution | ✅ Ready | Run multiple intents simultaneously |
| Microservices | ✅ Ready | Project + Service structure |
| Plugin System | ✅ Ready | Everything is replaceable |
| CLI Tools | ✅ Ready | `evo` command for project management |
| Authentication | ✅ Ready | Built-in auth processor |
| Caching | ✅ Ready | Intent-aware caching tiers |
| WebSocket | ✅ Ready | Real-time communication |
| Telegram Bot | ✅ Ready | Bot adapter included |

### What's Next? 🚀

The IOP runtime will expand beyond web development:

| Future Platform | Description |
|----------------|-------------|
| 🖥️ CLI Applications | Intent-driven command-line tools |
| 📱 Mobile | iOS/Android adapters |
| 🤖 AI Agents | Intent-based agent orchestration |
| 🎮 Game Engines | Real-time game logic |
| 📡 IoT | Edge device communication |
| 🔗 Blockchain | Decentralized intent processing |

**The language is an implementation detail. Intent is the platform.**

---

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

---

## Three Syntax Styles

All styles are IOP underneath — just different sugar.

### @route (Familiar) 🚀

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created"}
```

### @controller (For Large Projects) 🏗️

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": f"User {user_id}"}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created"}
```

### IOP Native (Full Control) 🎯

```python
from evoid import Intent, Level, add_intent

MY_INTENT = Intent(name="get_user", level=Level.STANDARD)

async def handler(intent: Intent) -> dict:
    return {"id": 1, "name": "Ali"}

add_intent(MY_INTENT, handler)
```

---

## Why IOP? 🤔

### The Problem

Every time you write a new endpoint, you have to decide:
- Which database? 🗄️
- How to cache? ⚡
- Should I encrypt this? 🔐
- What priority? 📊

**This is like being a chef who has to also build the kitchen, buy the groceries, and clean up — every single time you cook a meal.**

### The IOP Solution

What if your data could tell the kitchen what it needs?

```python
# Your data model IS your infrastructure policy
class Payment(BaseModel):
    card_number: critical(str)    # Auto-encrypt, audit, store safely
    amount: standard(float)       # Normal processing
    session_id: ephemeral(str)   # Memory only, auto-expire
```

**That's IOP. Your data tells the system what to do. You focus on what matters.**

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🎯 **Intent-Driven** | Declare what, framework decides how |
| ⚡ **Async-Native** | Full async/await support |
| 🧩 **Plugin-Based** | Everything is replaceable |
| 🔄 **Parallel Execution** | Run multiple intents simultaneously |
| 🏗️ **Microservices Ready** | Project + Service structure |
| 🔌 **Multi-Adapter** | ASGI, CLI, Telegram, Robyn, WebSocket |
| 📊 **Three Syntax Styles** | @route, @controller, IOP Native |
| 🔐 **Security Built-in** | Encryption, auth, audit trails |
| 💾 **Intent-Aware Caching** | EPHEMERAL, STANDARD, CRITICAL tiers |
| 📝 **Beautiful Logs** | Structured logging with loguru |

---

## CLI Commands

```bash
evo init <name>              # Create new project
evo service new <name>       # Add service to project
evo service list             # List services
evo service run <name>       # Run a service
evo sync                     # Sync dependencies
evo run                      # Run all services
evo serve                    # Quick serve
evo version                  # Show version
```

---

## Project Structure

```
my-api/
├── evoid.toml              # Project config
├── services/
│   ├── api/
│   │   ├── evoid.toml      # Service config
│   │   └── main.py         # Service code
│   └── worker/
│       ├── evoid.toml
│       └── main.py
└── shared/
    └── __init__.py         # Shared models
```

---

## Documentation

📖 **[Read the Docs](https://evoid.github.io/EVOID/)**

- [Getting Started](https://evoid.github.io/EVOID/#/tutorial/first-steps)
- [Why IOP?](https://evoid.github.io/EVOID/#/learn/why-iop)
- [API Reference](https://evoid.github.io/EVOID/#/api/)
- [Examples](https://evoid.github.io/EVOID/#/examples/)

---

## Contributing

We welcome contributions! EVOID is an open project and we'd love your help building the future of IOP.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

Apache 2.0

---

<p align="center">
  <strong>EVOID</strong> — Intent is the platform.<br>
  Built with 💜 by the EVOID Community
</p>
