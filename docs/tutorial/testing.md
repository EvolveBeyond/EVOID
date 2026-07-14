# Testing

Test your EVOID applications.

## Unit Test Example

```python
import pytest
from evoid.core import Intent, Level, Context, execute
from evoid.core.extend import add_intent_with_pipeline

def test_my_intent():
    # Setup
    intent = Intent(name="test", level=Level.EPHEMERAL)

    async def handler(ctx):
        return {"status": "ok"}

    add_intent_with_pipeline(intent, processors=["test"], handler=handler)

    # Execute
    result = asyncio.run(execute(intent))

    # Assert
    assert result.success is True
    assert result.value == {"status": "ok"}
```

## Override Dependencies

```python
from evoid import override, reset_overrides

# Override for testing
override("DatabaseService", MockDatabaseService())

# ... run tests ...

# Reset after tests
reset_overrides()
```

## Test Processors

```python
def test_rate_limiter():
    from evoid.processors.rate_limiter import process
    from evoid.core import Context, Intent, Level

    ctx = Context(
        intent=Intent(name="test", level=Level.STANDARD),
        metadata={"user_id": "user1"},
    )

    result = asyncio.run(process(ctx))
    assert result["allowed"] is True
```

## Why Test? 🤔

- ✅ **Catch bugs early** — Before they reach production
- ✅ **Document behavior** — Tests show how code works
- ✅ **Safe refactoring** — Change code without fear
- ✅ **CI/CD ready** — Automate testing

**Test your Intents, test your Processors, test your Pipelines.** 🧪
