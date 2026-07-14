"""Core tests — Verify IOP runtime works correctly."""

import asyncio
import pytest

from evoid.core import (
    Intent, Level, Context, Result,
    register, resolve, all_intents, clear_registry,
    register_processor, all_processors,
    execute, execute_by_name,
    PipelineConfig, resolve_pipeline,
)
from evoid.core.extend import (
    add_intent, add_intent_with_pipeline,
    before, after, before_processor, after_processor,
    get_pipeline_config, list_overrides, clear_overrides,
)
from evoid.core.parallel import gather, gather_with_priority, IntentQueue


# ============================================================
# Intent tests
# ============================================================

class TestIntent:
    def test_intent_creation(self):
        intent = Intent(name="test", level=Level.STANDARD)
        assert intent.name == "test"
        assert intent.level == Level.STANDARD

    def test_intent_frozen(self):
        intent = Intent(name="test", level=Level.CRITICAL)
        with pytest.raises(AttributeError):
            intent.name = "changed"

    def test_intent_registry(self):
        clear_registry()
        intent = Intent(name="test", level=Level.STANDARD)
        register(intent)
        assert resolve("test") is not None
        assert resolve("nonexistent") is None

    def test_all_intents(self):
        clear_registry()
        register(Intent(name="a", level=Level.STANDARD))
        register(Intent(name="b", level=Level.CRITICAL))
        assert len(all_intents()) == 2


# ============================================================
# Pipeline tests
# ============================================================

class TestPipeline:
    def test_resolve_pipeline(self):
        intent = Intent(name="test", level=Level.STANDARD)
        config = resolve_pipeline(intent)
        assert isinstance(config, PipelineConfig)
        assert len(config.processors) > 0

    def test_pipeline_override(self):
        clear_overrides()
        intent = Intent(name="test", level=Level.STANDARD)
        add_intent_with_pipeline(intent, processors=["a", "b", "c"])
        config = get_pipeline_config(intent)
        assert config.processors == ("a", "b", "c")


# ============================================================
# Execute tests
# ============================================================

class TestExecute:
    def test_execute_simple(self):
        clear_registry()
        intent = Intent(name="test", level=Level.EPHEMERAL)

        async def handler(ctx: Context) -> dict:
            return {"status": "ok"}

        add_intent_with_pipeline(intent, processors=["test"], handler=handler)

        result = asyncio.run(execute(intent))
        assert result.success is True
        assert result.value == {"status": "ok"}


# ============================================================
# Extend tests
# ============================================================

class TestExtend:
    def test_before_after(self):
        clear_overrides()
        before("test_route", "log_request")
        after("test_route", "log_response")
        overrides = list_overrides()
        assert "test_route" in overrides
        assert "log_request" in overrides["test_route"]

    def test_clear_overrides(self):
        clear_overrides()
        before("test", "proc")
        clear_overrides()
        assert len(list_overrides()) == 0


# ============================================================
# Parallel tests
# ============================================================

class TestParallel:
    def test_gather(self):
        clear_registry()
        intent1 = Intent(name="a", level=Level.STANDARD)
        intent2 = Intent(name="b", level=Level.STANDARD)

        async def handler(ctx: Context) -> dict:
            return {"ok": True}

        add_intent(intent1, handler)
        add_intent(intent2, handler)

        results = asyncio.run(gather(intent1, intent2))
        assert len(results) == 2
        assert all(r.success for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
