"""Web — Three syntax styles for web/backend development.

All styles are IOP underneath — just different syntax sugar.

1. @route: Function-based routes (get, post, put, delete)
2. @controller: Class-based controllers
3. native: IOP native approach

All convert to Intent → Pipeline → Result.
"""

from .route import (
    Service as RouteService,
    get,
    post,
    put,
    delete,
    run as run_route,
)
from .controller import (
    Service as ControllerService,
    Controller,
    GET,
    POST,
    PUT,
    DELETE,
    run as run_controller,
)
from .iop_style import (
    Service as NativeService,
    create_service,
    on,
    execute_service,
    run as run_native,
)

__all__ = [
    # @route syntax
    "RouteService",
    "get",
    "post",
    "put",
    "delete",
    "run_route",
    # @controller syntax
    "ControllerService",
    "Controller",
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "run_controller",
    # native syntax
    "NativeService",
    "create_service",
    "on",
    "execute_service",
    "run_native",
]
