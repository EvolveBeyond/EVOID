"""Web Pipeline — Auto-detect framework, wire native service to web adapter.

Usage:
    from evoid.native.pipeline import detect, create_web_pipeline

    pipeline = create_web_pipeline(service)
    await pipeline.run(port=8000)

Auto-detects: FastAPI/Starlette (ASGI) or Robyn.
Override: adapter="asgi" | "robyn"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class WebPipeline:
    """Web pipeline — wires native Service to web framework."""

    service: Any  # native.Service
    adapter: str = "auto"
    host: str = "0.0.0.0"
    port: int = 8000

    async def run(self, host: str | None = None, port: int | None = None) -> None:
        """Run the web pipeline."""
        h = host or self.host
        p = port or self.port

        if self.adapter == "robyn":
            await self._run_robyn(h, p)
        else:
            await self._run_asgi(h, p)

    async def _run_asgi(self, host: str, port: int) -> None:
        import uvicorn

        from ..adapters.asgi import create_app

        handlers = {}
        for intent in self.service.intents:
            handlers[intent.name] = self.service.handlers[intent.name]

        asgi_app = create_app(name=self.service.name, handlers=handlers)
        print(f"Starting {self.service.name} on http://{host}:{port}")
        uvicorn.run(asgi_app, host=host, port=port)

    async def _run_robyn(self, host: str, port: int) -> None:
        from ..adapters.robyn import create_app

        app = create_app(name=self.service.name)
        for intent in self.service.intents:
            handler = self.service.handlers[intent.name]
            method = intent.metadata.get("method", "GET").lower()
            path = intent.metadata.get("path", "/")

            route_fn = getattr(app, method, None)
            if route_fn:
                route_fn(path)(handler)

        app.start(host=host, port=port)


def detect() -> str:
    """Auto-detect which web framework is installed.

    Returns "robyn" if Robyn is installed, "asgi" otherwise.
    """
    try:
        import robyn  # noqa: F401
        return "robyn"
    except ImportError:
        return "asgi"


def create_web_pipeline(
    service: Any,
    adapter: str | None = None,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> WebPipeline:
    """Create a web pipeline for a native service.

    Args:
        service: native.Service with registered intents and handlers
        adapter: "auto" (default), "asgi", or "robyn"
        host: Bind host
        port: Bind port
    """
    resolved_adapter = adapter or detect()

    return WebPipeline(
        service=service,
        adapter=resolved_adapter,
        host=host,
        port=port,
    )
