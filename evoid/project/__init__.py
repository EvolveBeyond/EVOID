"""Project — Project management for microservices.

IOP: Project is just data + functions.
A project is a collection of services.
"""

from .manager import (
    init_project,
    add_service,
    list_services,
    get_project_config,
    ServiceInfo,
    ProjectInfo,
)
