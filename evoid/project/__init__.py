"""Project — Project management for microservices.

IOP: Project is just data + functions.
A project is a collection of services.
"""

from .manager import (
    ProjectInfo as ProjectInfo,
)
from .manager import (
    ServiceInfo as ServiceInfo,
)
from .manager import (
    add_service as add_service,
)
from .manager import (
    get_project_config as get_project_config,
)
from .manager import (
    init_project as init_project,
)
from .manager import (
    list_services as list_services,
)
