from functools import lru_cache

from api.v1.controllers.access_history import AccessHistoryController
from api.v1.controllers.auth import AuthController
from api.v1.controllers.health_check import HealthCheckController
from api.v1.controllers.oauth import FBOAuthController, GoogleOAuthController, YandexOAuthController
from api.v1.controllers.role import RoleController
from api.v1.controllers.user import UserController


@lru_cache
def get_auth_controller() -> AuthController:
    return AuthController()


@lru_cache
def get_yandex_oauth_controller() -> YandexOAuthController:
    return YandexOAuthController()


@lru_cache
def get_fb_oauth_controller() -> FBOAuthController:
    return FBOAuthController()


@lru_cache
def get_google_oauth_controller() -> GoogleOAuthController:
    return GoogleOAuthController()


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
