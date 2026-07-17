"""Contracts — Plugin interfaces. Pure types, no behavior.

IOP Principle: Plugins communicate through contracts.
These are just type definitions — the behavior lives in the engines.
"""

from .adapter import Adapter
from .cache import CacheEngine
from .schema import SchemaEngine
from .serializer import SerializerEngine
from .storage import StorageEngine

__all__ = [
    "SchemaEngine",
    "StorageEngine",
    "CacheEngine",
    "SerializerEngine",
    "Adapter",
]
