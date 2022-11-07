from functools import lru_cache

from services.auth_service import AuthService
from services.jwt_service import JWTService
from services.role_service import RoleService
from services.social_service import SocialAccountService
from services.user_service import UserService
from storage import (
    get_black_list_storage,
    get_jwt_storage,
    get_role_storage,
    get_social_storage,
    get_user_storage,
)


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(
        user_storage=get_user_storage(),
        jwt_storage=get_jwt_storage(),
        jwt_service=get_jwt_service(),
        black_list_storage=get_black_list_storage(),
    )


@lru_cache
def get_jwt_service() -> JWTService:
    return JWTService(
        jwt_storage=get_jwt_storage(), black_list_storage=get_black_list_storage()
    )


@lru_cache
def get_user_service() -> UserService:
    return UserService(user_storage=get_user_storage(), role_storage=get_role_storage())


@lru_cache
def get_role_service() -> RoleService:
    return RoleService(role_storage=get_role_storage())

@lru_cache()
def get_social_account_service() -> SocialAccountService:
    return SocialAccountService(social_storage=get_social_storage())
