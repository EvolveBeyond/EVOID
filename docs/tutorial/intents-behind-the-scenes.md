# Intents Behind the Scenes

What happens when you use decorators?

## The Magic ✨

When you write:

```python
@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}
```

Behind the scenes:

```
Step 1: @get("/users/{user_id}")
            ↓
Step 2: Intent created
        Intent(
            name="GET:/users/{user_id}",
            level=Level.STANDARD,
            metadata={"method": "GET", "path": "/users/{user_id}"}
        )
            ↓
Step 3: Intent registered
        register(intent)
            ↓
Step 4: Handler registered as processor
        register_processor("GET:/users/{user_id}", handler)
            ↓
Step 5: Ready to serve! 🚀
```

## See It Yourself

```python
from evoid.web.route import Service, get
from evoid.core import all_intents, all_processors

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}

# Print all registered intents
print("Intents:")
for name, intent in all_intents().items():
    print(f"  {name} [{intent.level.value}]")

# Print all registered processors
print("\nProcessors:")
for name in all_processors():
    print(f"  {name}")
```

Output:
```
Intents:
  GET:/users/{user_id} [standard]

Processors:
  GET:/users/{user_id}
```

**One decorator. Multiple automatic steps.** ✨
