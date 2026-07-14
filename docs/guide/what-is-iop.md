# What is IOP?

**Intent-Oriented Programming (IOP)** is a paradigm where:

- **Data carries its own intent** — the data tells the system what to do with it
- **Processors are independent** — they receive context, do their work, return
- **Pipeline routes by purpose** — intent determines the execution path

## The Problem with OOP/FP

```python
# OOP: You describe WHAT things ARE
class User:
    def save(self):
        self.db.save(self)  # ← Manual infrastructure decisions

# FP: You describe WHAT to DO
def save_user(user):
    encrypted = encrypt(user.email)      # Manual
    cache.set(f"user:{user.id}", encrypted)  # Manual
    db.insert("users", encrypted)        # Manual
```

**Both treat infrastructure as a separate concern that developers must handle manually.**

## The IOP Solution

```python
# IOP: You describe WHAT the data means
class User(BaseModel):
    name: standard(str)      # → Normal processing
    email: critical(str)     # → Auto-encrypt, audit, replicate
    session: ephemeral(str)  # → Memory only, auto-expire
```

**The framework handles infrastructure automatically based on intent.**

## Three Intent Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **EPHEMERAL** | Temporary, aggressive cache | Session data, tokens |
| **STANDARD** | Normal processing | Business data |
| **CRITICAL** | Strong consistency, encryption | Financial, auth data |

## Learn More

- [Intent](intent.md) — How intents work
- [Pipeline](pipeline.md) — How execution flows
- [Processors](processors.md) — How work gets done
