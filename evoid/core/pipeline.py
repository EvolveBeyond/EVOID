"""Pipeline — Pure function composition.

IOP Principle: Pipeline routes by purpose.
A pipeline is just a list of processor names executed in order.
No class, no state — just data in, result out.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

from .context import Context
from .processor import Processor


def _check_rejection(result: Any, name: str) -> Exception | None:
    """Check if a processor result signals rejection.

    Returns an Exception if rejected, None if ok.
    Security processors return {"authorized": False} on rejection.
    Schema processors return {"validated": False} on failure.
    """
    if not isinstance(result, dict):
        return None

    if result.get("authorized") is False:
        reason = result.get("reason", "unauthorized")
        return PermissionError(f"Rejected by {name}: {reason}")

    if result.get("validated") is False:
        error_msg = result.get("error", "validation failed")
        return ValueError(f"Validation failed in {name}: {error_msg}")

    return None

# Lazy import to avoid circular dependency
_events = None


def _get_events():
    global _events
    if _events is None:
        from . import events as _ev
        _events = _ev
    return _events


@dataclass(frozen=True)
class ProcessorResult:
    """What one processor did — pure data."""
    name: str
    duration: float
    input_state: dict[str, Any] = field(default_factory=dict)
    output_state: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Exception | None = None


@dataclass(frozen=True)
class Result:
    """Pipeline execution result — pure data."""

    success: bool
    value: Any = None
    error: Exception | None = None
    processors: tuple[str, ...] = ()
    duration: float = 0.0
    steps: tuple[ProcessorResult, ...] = ()
    warnings: tuple[str, ...] = ()


async def execute(
    pipeline: tuple[str, ...],
    context: Context,
    registry: dict[str, Processor],
    timeout: float | None = None,
    inspect: bool = False,
    strict: bool = False,
) -> Result:
    """Execute a pipeline of processors.

    Args:
        inspect: If True, capture per-processor state snapshots.
        strict: If True, raise LookupError when processor not found.
    """
    start = time.monotonic()
    ran: list[str] = []
    steps: list[ProcessorResult] = []
    warnings: list[str] = []
    result = None

    # Emit pre_execute event (zero cost when no hooks)
    ev = _get_events()
    if ev._has_hooks("pre_execute"):
        await ev.emit("pre_execute", context, {"pipeline": pipeline})

    try:
        if inspect:
            # Slow path — full inspection
            for name in pipeline:
                processor = registry.get(name)
                if processor is None:
                    msg = f"Pipeline: processor '{name}' not found in registry, skipping"
                    if strict:
                        return Result(
                            success=False,
                            error=LookupError(msg),
                            processors=tuple(ran),
                            warnings=tuple(warnings),
                            duration=time.monotonic() - start,
                        )
                    import logging
                    logging.warning(msg)
                    warnings.append(msg)
                    continue

                step_start = time.monotonic()
                input_state = context.state.copy()

                try:
                    result = await asyncio.wait_for(
                        processor(context),
                        timeout=timeout,
                    )

                    # Check if processor signals rejection
                    rejection = _check_rejection(result, name)
                    if rejection:
                        steps.append(ProcessorResult(
                            name=name,
                            duration=time.monotonic() - step_start,
                            input_state=input_state,
                            output_state=context.state.copy(),
                            success=False,
                            error=rejection,
                        ))
                        return Result(
                            success=False,
                            error=rejection,
                            steps=tuple(steps),
                            warnings=tuple(warnings),
                            duration=time.monotonic() - start,
                        )

                    ran.append(name)
                    steps.append(ProcessorResult(
                        name=name,
                        duration=time.monotonic() - step_start,
                        input_state=input_state,
                        output_state=context.state.copy(),
                        success=True,
                    ))
                except TimeoutError:
                    steps.append(ProcessorResult(
                        name=name,
                        duration=time.monotonic() - step_start,
                        input_state=input_state,
                        success=False,
                        error=TimeoutError(f"Processor '{name}' timed out after {timeout}s"),
                    ))
                    return Result(
                        success=False,
                        error=TimeoutError(f"Processor '{name}' timed out after {timeout}s"),
                        steps=tuple(steps),
                        warnings=tuple(warnings),
                        duration=time.monotonic() - start,
                    )
                except Exception as e:
                    steps.append(ProcessorResult(
                        name=name,
                        duration=time.monotonic() - step_start,
                        input_state=input_state,
                        success=False,
                        error=e,
                    ))
                    return Result(
                        success=False,
                        error=e,
                        steps=tuple(steps),
                        warnings=tuple(warnings),
                        duration=time.monotonic() - start,
                    )
            return Result(
                success=True,
                value=context.state,
                steps=tuple(steps),
                processors=tuple(ran),
                warnings=tuple(warnings),
                duration=time.monotonic() - start,
            )
        elif timeout is not None:
            # Medium path — timeout but no inspection
            for name in pipeline:
                processor = registry.get(name)
                if processor is None:
                    msg = f"Pipeline: processor '{name}' not found in registry, skipping"
                    if strict:
                        return Result(
                            success=False,
                            error=LookupError(msg),
                            processors=tuple(ran),
                            warnings=tuple(warnings),
                            duration=time.monotonic() - start,
                        )
                    import logging
                    logging.warning(msg)
                    warnings.append(msg)
                    continue

                try:
                    result = await asyncio.wait_for(
                        processor(context),
                        timeout=timeout,
                    )

                    # Check if processor signals rejection
                    rejection = _check_rejection(result, name)
                    if rejection:
                        return Result(
                            success=False,
                            error=rejection,
                            processors=tuple(ran),
                            warnings=tuple(warnings),
                            duration=time.monotonic() - start,
                        )

                    ran.append(name)
                except TimeoutError:
                    return Result(
                        success=False,
                        error=TimeoutError(f"Processor '{name}' timed out after {timeout}s"),
                        processors=tuple(ran),
                        warnings=tuple(warnings),
                        duration=time.monotonic() - start,
                    )
                except Exception as e:
                    return Result(
                        success=False,
                        error=e,
                        processors=tuple(ran),
                        warnings=tuple(warnings),
                        duration=time.monotonic() - start,
                    )
        else:
            # Fast path — no inspection, no timeout
            for name in pipeline:
                processor = registry.get(name)
                if processor is None:
                    msg = f"Pipeline: processor '{name}' not found in registry, skipping"
                    if strict:
                        return Result(
                            success=False,
                            error=LookupError(msg),
                            processors=tuple(ran),
                            warnings=tuple(warnings),
                            duration=time.monotonic() - start,
                        )
                    import logging
                    logging.warning(msg)
                    warnings.append(msg)
                    continue

                try:
                    result = await processor(context)

                    # Check if processor signals rejection
                    rejection = _check_rejection(result, name)
                    if rejection:
                        return Result(
                            success=False,
                            error=rejection,
                            processors=tuple(ran),
                            warnings=tuple(warnings),
                            duration=time.monotonic() - start,
                        )

                    ran.append(name)
                except Exception as e:
                    return Result(
                        success=False,
                        error=e,
                        processors=tuple(ran),
                        warnings=tuple(warnings),
                        duration=time.monotonic() - start,
                    )
    finally:
        # Emit post_execute event (always fires, even on failure)
        if ev._has_hooks("post_execute"):
            await ev.emit("post_execute", context, {
                "pipeline": pipeline,
                "success": result is not None,
                "processors": tuple(ran),
                "duration": time.monotonic() - start,
            })

    return Result(
        success=True,
        value=result,
        processors=tuple(ran),
        duration=time.monotonic() - start,
        steps=tuple(steps) if steps else (),
        warnings=tuple(warnings),
    )
