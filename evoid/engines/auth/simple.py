"""Simple Auth Engine — Token-based authorization.

IOP: Just functions. No class state.
"""

from __future__ import annotations

from typing import Any

# Simple token store
_tokens: dict[str, dict[str, Any]] = {}


def register_token(token: str, metadata: dict[str, Any]) -> None:
    """Register a token with metadata."""
    _tokens[token] = metadata


def verify(token: str) -> dict[str, Any] | None:
    """Verify a token, return metadata if valid."""
    return _tokens.get(token)


def revoke(token: str) -> bool:
    """Revoke a token."""
    if token in _tokens:
        del _tokens[token]
        return True
    return False


def clear() -> None:
    """Clear all tokens."""
    _tokens.clear()
