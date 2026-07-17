"""Loguru Logger Engine — Clean, beautiful logging.

IOP: Just wrapper functions. No class state.
Loguru provides beautiful out-of-the-box formatting.
"""

from __future__ import annotations

from typing import Any

try:
    from loguru import logger as _loguru_logger
    _HAS_LOGURU = True
except ImportError:
    _HAS_LOGURU = False
    _loguru_logger = None


def init(
    name: str = "evoid",
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "7 days",
    format: str | None = None,
) -> None:
    """Initialize loguru logger.

    Args:
        name: Service name for log context
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        rotation: When to rotate log files
        retention: How long to keep log files
        format: Custom format string (None = default beautiful format)
    """
    if not _HAS_LOGURU:
        return

    # Remove default handler
    _loguru_logger.remove()

    # Default beautiful format
    if format is None:
        format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add console handler
    _loguru_logger.add(
        sink=None,  # stderr
        format=format,
        level=level,
        colorize=True,
    )

    # Add context
    _loguru_logger.configure(extra={"service": name})


def bind(**kwargs: Any) -> None:
    """Bind extra context to logger."""
    if _HAS_LOGURU:
        _loguru_logger.configure(extra=kwargs)


def info(msg: str, **kwargs: Any) -> None:
    """Log info."""
    if _HAS_LOGURU:
        _loguru_logger.info(msg, **kwargs)


def error(msg: str, **kwargs: Any) -> None:
    """Log error."""
    if _HAS_LOGURU:
        _loguru_logger.error(msg, **kwargs)


def warning(msg: str, **kwargs: Any) -> None:
    """Log warning."""
    if _HAS_LOGURU:
        _loguru_logger.warning(msg, **kwargs)


def debug(msg: str, **kwargs: Any) -> None:
    """Log debug."""
    if _HAS_LOGURU:
        _loguru_logger.debug(msg, **kwargs)


def critical(msg: str, **kwargs: Any) -> None:
    """Log critical."""
    if _HAS_LOGURU:
        _loguru_logger.critical(msg, **kwargs)


def intent(intent_name: str, level: str, msg: str, **kwargs: Any) -> None:
    """Log with intent context.

    Beautiful formatted log like:
    2026-07-14 12:00:00.000 | INFO     | process_payment | CRITICAL | Payment processed
    """
    if _HAS_LOGURU:
        _loguru_logger.log(
            level,
            f"[{intent_name}] {msg}",
            **kwargs,
        )


def pipeline(intent_name: str, processors: tuple[str, ...], success: bool, duration: float) -> None:
    """Log pipeline execution.

    Beautiful formatted log like:
    2026-07-14 12:00:00.000 | INFO     | process_payment | ✓ validate → authorize → audit (0.003s)
    """
    status = "✓" if success else "✗"
    chain = " → ".join(processors)
    msg = f"{status} {chain} ({duration:.3f}s)"

    if _HAS_LOGURU:
        if success:
            _loguru_logger.info(f"[{intent_name}] {msg}")
        else:
            _loguru_logger.error(f"[{intent_name}] {msg}")


def request(method: str, path: str, status: int, duration: float) -> None:
    """Log HTTP request.

    Beautiful formatted log like:
    2026-07-14 12:00:00.000 | INFO     | POST /payments 200 (0.003s)
    """
    msg = f"{method} {path} {status} ({duration:.3f}s)"

    if _HAS_LOGURU:
        _loguru_logger.info(msg)
