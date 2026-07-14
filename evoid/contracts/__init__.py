"""Contracts — Plugin interfaces. Pure types, no behavior.

IOP Principle: Plugins communicate through contracts.
These are just type definitions — the behavior lives in the engines.
"""

from .schema import SchemaEngine
from .storage import StorageEngine
from .cache import CacheEngine
from .serializer import SerializerEngine
from .adapter import Adapter

__all__ = [
    "SchemaEngine",
    "StorageEngine",
    "CacheEngine",
    "SerializerEngine",
    "Adapter",
]
