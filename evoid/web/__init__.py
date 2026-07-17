"""Web — Web-specific features for EVOID services.

Primary entry points:
    evoid.native        — IOP mother syntax (adapter-agnostic)
    evoid.web.route     — Function-based routes (@get, @post)
    evoid.web.controller — Class-based controllers (@Controller)
    evoid.web.pipeline  — Web pipeline (auto-detect framework)

Backward-compat aliases:
    from evoid.web import NativeService, create_service  → use evoid.native
    from evoid.web import RouteService, get, post        → use evoid.web.route
    from evoid.web import ControllerService, Controller  → use evoid.web.controller
"""

from ..native import (
    Service as NativeService,
)
from ..native import (
    create_service,
    execute_service,
    on,
)
from ..native import (
    run as run_native,
)
from ..native.pipeline import (
    WebPipeline,
    create_web_pipeline,
    detect,
)
from .controller import (
    DELETE,
    GET,
    POST,
    PUT,
    Controller,
)
from .controller import (
    App as ControllerApp,
)
from .controller import (
    Service as ControllerService,
)
from .controller import (
    run as run_controller,
)
from .route import (
    App as RouteApp,
)
from .route import (
    Service as RouteService,
)
from .route import (
    after,
    after_handler,
    before,
    before_handler,
    delete,
    get,
    post,
    put,
    replace_pipeline,
)
from .route import (
    run as run_route,
)

__all__ = [
    # Native IOP syntax (from evoid.native)
    "NativeService",
    "create_service",
    "on",
    "execute_service",
    "run_native",
    # @route syntax
    "RouteService",
    "RouteApp",
    "get",
    "post",
    "put",
    "delete",
    "before",
    "after",
    "before_handler",
    "after_handler",
    "replace_pipeline",
    "run_route",
    # @controller syntax
    "ControllerService",
    "ControllerApp",
    "Controller",
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "run_controller",
    # Web pipeline
    "WebPipeline",
    "detect",
    "create_web_pipeline",
]
