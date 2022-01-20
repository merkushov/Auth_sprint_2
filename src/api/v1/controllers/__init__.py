from functools import lru_cache

from api.v1.controllers.auth import AuthController
from api.v1.controllers.health_check import HealthCheckController
from api.v1.controllers.access_history import AccessHistoryController
from api.v1.controllers.role import RoleController
from api.v1.controllers.user import UserController


@lru_cache
def get_auth_controller() -> AuthController:
    return AuthController()


@lru_cache
def get_health_check_controller() -> HealthCheckController:
    return HealthCheckController()


@lru_cache
def get_access_history_controller() -> AccessHistoryController:
    return AccessHistoryController()


@lru_cache
def get_role_controller() -> RoleController:
    return RoleController()


@lru_cache
def get_user_controller() -> UserController:
    return UserController()
