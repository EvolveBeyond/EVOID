"""ASGI Adapter — Converts HTTP requests to Intents.

IOP: Adapter is a function that maps data to Intent.
This adapter creates a Starlette/ASGI app that:
1. Receives HTTP request
2. Converts to Intent
3. Executes through pipeline
4. Returns response

Route decorators (get, post, put, delete) live HERE because
param extraction is adapter-specific. Each adapter decides how
to pull params from its request type.
"""

from __future__ import annotations

import json
import time
from collections.abc import Awaitable, Callable
from typing import Any

from ..core import Context, register, register_processor
from ..core.extend import replace_pipeline
from ..core.intent import Intent, Level
from ..core.resolver import PipelineConfig, _DEFAULT_PROCESSORS
from ..core.runtime import execute

# Handler type: takes Intent, returns result
Handler = Callable[[Intent], Awaitable[Any]]


def create_app(
    name: str = "evoid-service",
    handlers: dict[str, Handler] | None = None,
) -> Any:
    """Create an ASGI application.

    Args:
        name: Service name
        handlers: Intent name → handler function mapping

    Returns:
        ASGI application (Starlette)
    """
    try:
        from starlette.applications import Starlette
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from starlette.routing import Route
    except ImportError:
        raise ImportError("starlette required for ASGI adapter: pip install starlette")

    _handlers = handlers or {}

    async def health_endpoint(request: Request) -> JSONResponse:
        """Health check endpoint."""
        return JSONResponse({"status": "healthy", "service": name})

    async def intent_endpoint(request: Request) -> JSONResponse:
        """Handle any request as an Intent."""
        start = time.monotonic()

        # Parse request
        method = request.method
        path = request.url.path

        # Read body
        body = b""
        if method in ("POST", "PUT", "PATCH"):
            body = await request.body()

        # Get only needed headers
        headers = {
            "authorization": request.headers.get("authorization", ""),
            "x-intent-level": request.headers.get("x-intent-level", ""),
            "x-forwarded-for": request.headers.get("x-forwarded-for", ""),
            "content-type": request.headers.get("content-type", ""),
        }

        # Get query params
        query = dict(request.query_params) if hasattr(request, "query_params") else {}

        # Convert to Intent
        intent = _intent_from_request(method, path, body, headers, query=query)

        # Find handler — exact match first, then pattern match
        intent_name, path_params = _match_intent(method, path, _handlers)

        # Rebuild intent if pattern matched (with extracted params)
        if path_params:
            intent = _intent_from_request(method, path, body, headers, query=query, path_params=path_params)
            # Override intent name with the matched pattern
            intent = Intent(
                name=intent_name,
                level=intent.level,
                metadata={**intent.metadata, "params": path_params},
            )

        handler = _handlers.get(intent_name) if intent_name else None

        try:
            if handler:
                # Register handler as processor and compose pipeline
                # Wrap: pipeline passes Context, user handler expects Intent
                async def _adapted(ctx: Context) -> Any:
                    return await handler(ctx.intent)
                register_processor(intent.name, _adapted)
                security = _DEFAULT_PROCESSORS.get(intent.level, ())
                replace_pipeline(intent.name, [*security, intent.name])

            # Always execute through pipeline
            pipeline_result = await execute(intent)
            if pipeline_result.success:
                result = pipeline_result.value
            else:
                return JSONResponse(
                    {"error": str(pipeline_result.error)},
                    status_code=500,
                )

            duration = time.monotonic() - start

            return JSONResponse({
                "status": "success",
                "intent": intent.name,
                "level": intent.level.value,
                "result": result,
                "duration": round(duration, 3),
            })

        except Exception as e:
            return JSONResponse(
                {"error": str(e)},
                status_code=500,
            )

    # Create routes
    routes = [
        Route("/health", health_endpoint, methods=["GET"]),
        Route("/{path:path}", intent_endpoint, methods=["GET", "POST", "PUT", "DELETE", "PATCH"]),
    ]

    return Starlette(routes=routes)


def _intent_from_request(
    method: str,
    path: str,
    body: bytes,
    headers: dict[str, str],
    query: dict[str, str] | None = None,
    path_params: dict[str, str] | None = None,
) -> Intent:
    """Convert HTTP request to Intent."""
    # Parse body
    data = {}
    if body:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"raw": body.decode("utf-8", errors="replace")}

    # Determine level from headers
    level = Level.STANDARD
    intent_header = headers.get("x-intent-level", "").lower()
    if intent_header == "critical":
        level = Level.CRITICAL
    elif intent_header == "ephemeral":
        level = Level.EPHEMERAL

    # Create intent name from method + path
    name = f"{method.upper()}:{path}"

    # Merge path params + query params into metadata
    params = {}
    if path_params:
        params.update(path_params)
    if query:
        params.update(query)

    return Intent(
        name=name,
        level=level,
        metadata={
            "method": method,
            "path": path,
            "body": data,
            "headers": headers,
            "params": params,
        },
    )


def _match_path(template: str, path: str) -> dict[str, str] | None:
    """Match a path template like /users/{id} against /users/42.

    Returns extracted params dict, or None if no match.
    """
    template_parts = template.strip("/").split("/")
    path_parts = path.strip("/").split("/")

    if len(template_parts) != len(path_parts):
        return None

    params = {}
    for t, p in zip(template_parts, path_parts):
        if t.startswith("{") and t.endswith("}"):
            params[t[1:-1]] = p
        elif t != p:
            return None

    return params


def _match_intent(
    method: str,
    path: str,
    handlers: dict[str, Handler],
) -> tuple[str | None, dict[str, str]]:
    """Match request against handler keys with path template support.

    Returns (intent_name, extracted_params) or (None, {}).
    """
    # 1. Exact match (fast path)
    exact = f"{method.upper()}:{path}"
    if exact in handlers:
        return exact, {}

    # 2. Pattern match against handler keys
    for pattern in handlers:
        if ":" not in pattern:
            continue
        pattern_method, pattern_path = pattern.split(":", 1)
        if pattern_method.upper() != method.upper():
            continue
        params = _match_path(pattern_path, path)
        if params is not None:
            return pattern, params

    return None, {}


def run(
    name: str = "evoid-service",
    handlers: dict[str, Handler] | None = None,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> None:
    """Run the ASGI server.

    Convenience function to create and run the app.
    """
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn required: pip install uvicorn")

    app = create_app(name=name, handlers=handlers)
    print(f"Starting {name} on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


# ============================================================
# Route decorators — adapter-specific
# ============================================================


def get(path: str, level: str = "standard") -> Callable:
    """GET route — creates Intent, registers ASGI handler."""
    def decorator(func: Handler) -> Handler:
        from ..web._shared import create_intent as _create_intent
        from ..core.annotations import apply_annotations, validate_annotations

        intent = _create_intent("GET", path, level)
        register(intent)

        # Read and validate annotations
        ann = apply_annotations(func)
        errors = validate_annotations(func)
        if errors:
            import logging
            for e in errors:
                logging.error("Annotation error on %s: %s", func.__name__, e)

        async def processor(ctx: Context) -> Any:
            params = ctx.metadata.get("params", {})
            return await func(**params)

        register_processor(intent.name, processor)

        # Compose pipeline: use annotation pipeline if specified, else defaults
        if ann["pipeline"]:
            pipeline = ann["pipeline"]
        else:
            security = _DEFAULT_PROCESSORS.get(intent.level, ())
            pipeline = [*security, intent.name]

        replace_pipeline(intent.name, pipeline)

        # Apply annotation timeout if specified
        if ann["timeout"] is not None:
            from ..core.extend import _pipeline_overrides
            existing = _pipeline_overrides.get(intent.name)
            if existing:
                _pipeline_overrides[intent.name] = PipelineConfig(
                    processors=existing.processors,
                    priority=existing.priority,
                    timeout=ann["timeout"],
                    metadata=existing.metadata,
                )

        return func
    return decorator


def post(path: str, level: str = "standard") -> Callable:
    """POST route — creates Intent, registers ASGI handler."""
    def decorator(func: Handler) -> Handler:
        from ..web._shared import create_intent as _create_intent
        from ..core.annotations import apply_annotations, validate_annotations

        intent = _create_intent("POST", path, level)
        register(intent)

        # Read and validate annotations
        ann = apply_annotations(func)
        errors = validate_annotations(func)
        if errors:
            import logging
            for e in errors:
                logging.error("Annotation error on %s: %s", func.__name__, e)

        async def processor(ctx: Context) -> Any:
            if "body" not in ctx.metadata:
                raise ValueError(f"POST {path}: missing request body in context metadata")
            body = ctx.metadata["body"]
            return await func(**body)

        register_processor(intent.name, processor)

        # Compose pipeline: use annotation pipeline if specified, else defaults
        if ann["pipeline"]:
            pipeline = ann["pipeline"]
        else:
            security = _DEFAULT_PROCESSORS.get(intent.level, ())
            pipeline = [*security, intent.name]

        replace_pipeline(intent.name, pipeline)

        # Apply annotation timeout if specified
        if ann["timeout"] is not None:
            from ..core.extend import _pipeline_overrides
            existing = _pipeline_overrides.get(intent.name)
            if existing:
                _pipeline_overrides[intent.name] = PipelineConfig(
                    processors=existing.processors,
                    priority=existing.priority,
                    timeout=ann["timeout"],
                    metadata=existing.metadata,
                )

        return func
    return decorator


def put(path: str, level: str = "standard") -> Callable:
    """PUT route — creates Intent, registers ASGI handler."""
    def decorator(func: Handler) -> Handler:
        from ..web._shared import create_intent as _create_intent
        from ..core.annotations import apply_annotations, validate_annotations

        intent = _create_intent("PUT", path, level)
        register(intent)

        ann = apply_annotations(func)
        errors = validate_annotations(func)
        if errors:
            import logging
            for e in errors:
                logging.error("Annotation error on %s: %s", func.__name__, e)

        async def processor(ctx: Context) -> Any:
            if "body" not in ctx.metadata:
                raise ValueError(f"PUT {path}: missing request body in context metadata")
            body = ctx.metadata["body"]
            return await func(**body)

        register_processor(intent.name, processor)

        if ann["pipeline"]:
            pipeline = ann["pipeline"]
        else:
            security = _DEFAULT_PROCESSORS.get(intent.level, ())
            pipeline = [*security, intent.name]

        replace_pipeline(intent.name, pipeline)

        if ann["timeout"] is not None:
            from ..core.extend import _pipeline_overrides
            existing = _pipeline_overrides.get(intent.name)
            if existing:
                _pipeline_overrides[intent.name] = PipelineConfig(
                    processors=existing.processors,
                    priority=existing.priority,
                    timeout=ann["timeout"],
                    metadata=existing.metadata,
                )

        return func
    return decorator


def delete(path: str, level: str = "standard") -> Callable:
    """DELETE route — creates Intent, registers ASGI handler."""
    def decorator(func: Handler) -> Handler:
        from ..web._shared import create_intent as _create_intent
        from ..core.annotations import apply_annotations, validate_annotations

        intent = _create_intent("DELETE", path, level)
        register(intent)

        ann = apply_annotations(func)
        errors = validate_annotations(func)
        if errors:
            import logging
            for e in errors:
                logging.error("Annotation error on %s: %s", func.__name__, e)

        async def processor(ctx: Context) -> Any:
            params = ctx.metadata.get("params", {})
            return await func(**params)

        register_processor(intent.name, processor)

        if ann["pipeline"]:
            pipeline = ann["pipeline"]
        else:
            security = _DEFAULT_PROCESSORS.get(intent.level, ())
            pipeline = [*security, intent.name]

        replace_pipeline(intent.name, pipeline)

        if ann["timeout"] is not None:
            from ..core.extend import _pipeline_overrides
            existing = _pipeline_overrides.get(intent.name)
            if existing:
                _pipeline_overrides[intent.name] = PipelineConfig(
                    processors=existing.processors,
                    priority=existing.priority,
                    timeout=ann["timeout"],
                    metadata=existing.metadata,
                )

        return func
    return decorator
