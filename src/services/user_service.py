from uuid import UUID

import exceptions as exc
from models.api.user import AccessHistory, InputCreateUser, InputUpdateUser, User
from storage import IUserStorage
from storage.role_storage import IRoleStorage
from utils.password import password_hash


class UserService:
    """Класс сервиса Пользователя.

    Содержит общий код, для работы с сущностью Пользователь.
    """

    def __init__(
        self,
        user_storage: IUserStorage,
        role_storage: IRoleStorage,
    ):
        self.user_storage = user_storage
        self.role_storage = role_storage

    def get_user(self, **user_kwargs) -> User:
        """Найти пользователя по имени."""

        db_user = self.user_storage.get_user(**user_kwargs)

        user = User.from_orm(db_user)

        return user

    def create_user(self, user: InputCreateUser) -> User:
        """Создать нового пользователя."""

        db_user: User = self.user_storage.create_user(
            username=user.username,
            email=user.email,
            password_hash=password_hash(user.password),
        )

        created_user = User.from_orm(db_user)

        return created_user

    def update_user(self, user: InputUpdateUser) -> User:
        """Обновить данные существующего пользователя."""

        user_data = dict()
        if user.username:
            user_data.setdefault("username", user.username)
        if user.email:
            user_data.setdefault("email", user.email)
        if user.password:
            user_data.setdefault("password_hash", password_hash(user.password))

        db_updated_user = self.user_storage.update_user(id=user.id, raw_data=user_data)

        updated_user = User.from_orm(db_updated_user)

        return updated_user

    def set_role(self, role: str, user_name: str):
        self.user_storage.set_user_role(role, user_name)

    def validate_password(self, user: User, password: str) -> None:
        """Проверка пароля Пользователя."""

        encoded_password = password_hash(password)
        if encoded_password != user.password_hash:
            raise exc.ApiLoginInvalidParamsException

        return None

    def create_access_history(self, user: User, user_agent: str) -> None:
        """Сохранить факт входа пользователя в свой аккаунт."""

        self.user_storage.store_user_login_history(user_id=user.id, info=user_agent)

        return None

    def get_user_access_history(self, user_id: UUID) -> list:
        """Получить историю входов Пользователя по его идентификатору."""

        db_history = self.user_storage.get_user_history(user_id=user_id)

        history = []
        for item in db_history:
            history.append(
                AccessHistory(
                    user_agent=item.info,
                    datetime=item.created_at,
                )
            )

        return history

    def set_role_to_user(self, user_id: UUID, role_id: UUID) -> None:
        """Задать Роль Пользователю."""

        db_role = self.role_storage.get_role(role_id=role_id)
        db_user = self.user_storage.get_user(id=user_id)

        self.user_storage.set_role_to_user(user=db_user, role=db_role)

        return None

    def check_user_role(self, user_id: UUID, role_id: UUID) -> bool:
        """Проверить наличие Роли у Пользователя."""
        db_user = self.user_storage.get_user(id=user_id)

        has_role = False
        for role in db_user.roles:
            if str(role.id) == str(role_id):
                has_role = True
                break

        return has_role

    def delete_user_role(self, user_id: UUID, role_id: UUID) -> None:
        """Удалить Роль Пользователю."""
        db_role = self.role_storage.get_role(role_id=role_id)
        db_user = self.user_storage.get_user(id=user_id)

        self.user_storage.delete_user_role(user=db_user, role=db_role)

        return None

    def get_user_by_social_id(self, social_name, social_id):
        return self.user_storage.get_user_by_social_id(social_name=social_name, social_id=social_id)
