"""Structlog Logger Engine — Uses stdlib logging.

IOP: Just wrapper functions. No class state.
"""

from __future__ import annotations

import logging
from typing import Any

_logger: logging.Logger | None = None


def init(name: str = "evoid", level: int = logging.INFO) -> None:
    """Initialize logger."""
    global _logger
    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    if not _logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        ))
        _logger.addHandler(handler)


def info(msg: str, **kwargs: Any) -> None:
    """Log info."""
    if _logger:
        _logger.info(msg, **kwargs)


def error(msg: str, **kwargs: Any) -> None:
    """Log error."""
    if _logger:
        _logger.error(msg, **kwargs)


def warning(msg: str, **kwargs: Any) -> None:
    """Log warning."""
    if _logger:
        _logger.warning(msg, **kwargs)


def debug(msg: str, **kwargs: Any) -> None:
    """Log debug."""
    if _logger:
        _logger.debug(msg, **kwargs)
