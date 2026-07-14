"""Pipeline — Pure function composition.

IOP Principle: Pipeline routes by purpose.
A pipeline is just a list of processor names executed in order.
No class, no state — just data in, result out.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

from .context import Context
from .processor import Processor


@dataclass(frozen=True)
class Result:
    """Pipeline execution result — pure data.

    Attributes:
        success: Did it complete?
        value: The result (None if failed)
        error: The exception (None if succeeded)
        processors: Which processors ran
        duration: How long it took
    """

    success: bool
    value: Any = None
    error: Exception | None = None
    processors: tuple[str, ...] = ()
    duration: float = 0.0


async def execute(
    pipeline: tuple[str, ...],
    context: Context,
    registry: dict[str, Processor],
    timeout: float | None = None,
) -> Result:
    """Execute a pipeline of processors.

    Pure function: takes data, returns data.
    No class, no state, no side effects (except processor execution).
    """
    start = time.monotonic()
    ran: list[str] = []
    result = None

    for name in pipeline:
        processor = registry.get(name)
        if processor is None:
            continue

        try:
            result = await asyncio.wait_for(
                processor(context),
                timeout=timeout,
            )
            ran.append(name)
        except asyncio.TimeoutError:
            return Result(
                success=False,
                error=TimeoutError(f"Processor '{name}' timed out after {timeout}s"),
                processors=tuple(ran),
                duration=time.monotonic() - start,
            )
        except Exception as e:
            return Result(
                success=False,
                error=e,
                processors=tuple(ran),
                duration=time.monotonic() - start,
            )

    return Result(
        success=True,
        value=result,
        processors=tuple(ran),
        duration=time.monotonic() - start,
    )
