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


async def execute(
    pipeline: tuple[str, ...],
    context: Context,
    registry: dict[str, Processor],
    timeout: float | None = None,
    inspect: bool = False,
) -> Result:
    """Execute a pipeline of processors.

    Args:
        inspect: If True, capture per-processor state snapshots.
    """
    start = time.monotonic()
    ran: list[str] = []
    steps: list[ProcessorResult] = []
    result = None

    for name in pipeline:
        processor = registry.get(name)
        if processor is None:
            continue

        step_start = time.monotonic()
        input_state = context.state.copy() if inspect else {}

        try:
            result = await asyncio.wait_for(
                processor(context),
                timeout=timeout,
            )
            ran.append(name)

            steps.append(ProcessorResult(
                name=name,
                duration=time.monotonic() - step_start,
                input_state=input_state,
                output_state=context.state.copy() if inspect else {},
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
                processors=tuple(ran),
                duration=time.monotonic() - start,
                steps=tuple(steps),
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
                processors=tuple(ran),
                duration=time.monotonic() - start,
                steps=tuple(steps),
            )

    return Result(
        success=True,
        value=result,
        processors=tuple(ran),
        duration=time.monotonic() - start,
        steps=tuple(steps),
    )
