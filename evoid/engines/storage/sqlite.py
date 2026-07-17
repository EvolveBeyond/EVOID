"""SQLite Storage Engine — Persistent storage with SQLite.

IOP: Simple async wrapper. No class inheritance.
"""

from __future__ import annotations

import json
from typing import Any

try:
    import aiosqlite
    HAS_AIODELETE = True
except ImportError:
    HAS_AIODELETE = False


# Default database path
_db_path: str = "evoid.db"
_db: Any = None


async def init(db_path: str = "evoid.db") -> None:
    """Initialize SQLite connection."""
    global _db, _db_path
    _db_path = db_path
    if HAS_AIODELETE:
        _db = await aiosqlite.connect(db_path)
        await _db.execute("""
            CREATE TABLE IF NOT EXISTS store (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        await _db.commit()


async def read(key: str) -> Any | None:
    """Read from SQLite."""
    if _db is None:
        return None
    async with _db.execute("SELECT value FROM store WHERE key = ?", (key,)) as cursor:
        row = await cursor.fetchone()
        if row:
            return json.loads(row[0])
    return None


async def write(key: str, value: Any) -> bool:
    """Write to SQLite."""
    if _db is None:
        return False
    await _db.execute(
        "INSERT OR REPLACE INTO store (key, value) VALUES (?, ?)",
        (key, json.dumps(value)),
    )
    await _db.commit()
    return True


async def delete(key: str) -> bool:
    """Delete from SQLite."""
    if _db is None:
        return False
    await _db.execute("DELETE FROM store WHERE key = ?", (key,))
    await _db.commit()
    return True


async def health() -> bool:
    """Check SQLite health."""
    return _db is not None


async def close() -> None:
    """Close SQLite connection."""
    global _db
    if _db:
        await _db.close()
        _db = None
