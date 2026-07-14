# Caching

Add caching to your API.

## Using Cache Engine

```python
from evoid.engines.cache import memory as cache

# Set cache
await cache.set("user:123", {"name": "Ali"}, ttl=300.0)

# Get cache
user = await cache.get("user:123")

# Delete cache
await cache.delete("user:123")
```

## Cache with Intent Level

Different intent levels have different caching strategies:

| Level | Cache Strategy |
|-------|---------------|
| EPHEMERAL | Memory only, aggressive (5 min) |
| STANDARD | Balanced (1 hour) |
| CRITICAL | Write-through to all tiers |

## Custom Cache Processor

```python
from evoid.core import Context
from evoid.engines.cache import memory as cache

async def cache_processor(ctx: Context) -> dict:
    """Cache based on intent level."""
    key = f"{ctx.intent.name}:{ctx.intent.metadata}"

    # Check cache first
    cached = await cache.get(key)
    if cached:
        ctx.state["cached"] = True
        return cached

    # Not in cache, continue pipeline
    ctx.state["cached"] = False
    return {"cached": False}

register_processor("cache", cache_processor)
```

## Why Caching? 🤔

- ✅ **Faster** — Read from cache instead of database
- ✅ **Cheaper** — Less database load
- ✅ **Scalable** — Handle more requests
- Intent-driven: Level determines caching strategy

**Cache is just another processor.** ⚡
