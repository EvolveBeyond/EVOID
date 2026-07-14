"""Adapter — Interface for runtime adapters.

IOP: Contract only. Behavior lives in adapters/.
Adapters convert external events into Intents.
"""

from __future__ import annotations

from typing import Any, Protocol

from ..core.intent import Intent


class Adapter(Protocol):
    """Protocol for runtime adapters.

    Adapters convert external events (HTTP, CLI, MQTT, etc.)
    into Intents that the runtime can execute.
    """

    def intent_from(self, event: Any) -> Intent: ...
    def response_from(self, result: Any) -> Any: ...
