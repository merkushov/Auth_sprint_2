from functools import lru_cache

from storage.black_list import IBlackListStorage, RedisBlackListStorage
from storage.jwt_storage import IJwtStorage, PostgresJwtStorage
from storage.role_storage import IRoleStorage, PostgresRoleStorage
from storage.social_storage import PostgresSocialAccountStorage
from storage.user_storage import IUserStorage, PostgresUserStorage


@lru_cache
def get_black_list_storage() -> IBlackListStorage:
    return RedisBlackListStorage()


@lru_cache
def get_user_storage() -> IUserStorage:
    return PostgresUserStorage()


@lru_cache
def get_jwt_storage() -> IJwtStorage:
    return PostgresJwtStorage()


@lru_cache
def get_role_storage() -> IRoleStorage:
    return PostgresRoleStorage()


@lru_cache
def get_social_storage() -> PostgresSocialAccountStorage:
    return PostgresSocialAccountStorage()
