from storage.black_list import IBlackListStorage, RedisBlackListStorage
from storage.jwt_storage import IJwtStorage, PostgresJwtStorage
from storage.role_storage import IRoleStorage, PostgresRoleStorage
from storage.user_storage import IUserStorage, PostgresUserStorage


def get_black_list_storage() -> IBlackListStorage:
    return RedisBlackListStorage()


def get_user_storage() -> IUserStorage:
    return PostgresUserStorage()


def get_jwt_storage() -> IJwtStorage:
    return PostgresJwtStorage()


def get_role_storage() -> IRoleStorage:
    return PostgresRoleStorage()
