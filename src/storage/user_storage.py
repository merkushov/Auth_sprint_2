import abc
from typing import Optional
from uuid import UUID

import sqlalchemy as sa

import exceptions as exc
from db import db
from exceptions import (
    ApiEmailInUseException,
    ApiLoginInUseException,
    ApiUserAlreadyExistsException,
    ApiUserNotFoundException,
)
from models.db.auth_model import LoginHistory, Role, User


class IUserStorage:
    """Базовый абстрактный класс хранилища данных о пользователе."""

    @abc.abstractmethod
    def get_user(
        self, id: Optional[str] = None, username: Optional[str] = None, **user_kwargs
    ) -> User:
        """Получить данные пользователе."""

    @abc.abstractmethod
    def get_user_history(self, user_id: UUID) -> list[LoginHistory]:
        """Получить данные из login_history по ключу user_id."""

    @abc.abstractmethod
    def create_user(self, username: str, email: str, password_hash: str) -> User:
        """Создать нового пользователя."""

    @abc.abstractmethod
    def update_user(self, id: UUID, raw_data: dict) -> User:
        """Обновить существующего пользователя по его идентификатору."""

    @abc.abstractmethod
    def store_user_login_history(self, user_id: UUID, info: str) -> None:
        """Сохранить информацию о факте логина Пользователя."""

    @abc.abstractmethod
    def set_user_role(self, role_name: str, user_name: str):
        """Установить пользователю роль.

        :param role_name: имя роли
        :param user_name: имя пользователя
        """

    @abc.abstractmethod
    def set_role_to_user(self, user: User, role: Role) -> None:
        """Установить Роль Пользователю."""

    @abc.abstractmethod
    def delete_user_role(self, user: User, role: Role) -> None:
        """Удалить Роль Пользователю."""


class PostgresUserStorage(IUserStorage):
    def create_user(self, username: str, email: str, password_hash: str) -> User:
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)

        try:
            db.session.commit()
        except sa.exc.IntegrityError as exception:
            raise ApiUserAlreadyExistsException(
                detail=exception.orig.diag.message_detail
            )

        db.session.refresh(user)

        return user

    def update_user(self, id: UUID, raw_data: dict) -> User:
        stmt = sa.update(User).filter(User.id == id).values(**raw_data)

        try:
            db.session.execute(stmt)
            db.session.commit()
        except sa.exc.IntegrityError as exception:
            raise ApiUserNotFoundException(detail=exception.orig.diag.message_detail)

        user = self.get_user(id=id)

        return user

    def _user_credentials_validation(self, username: str, email: str) -> None:
        existed_user = self.get_user(username=username)

        if existed_user:
            raise ApiLoginInUseException

        user_from_db = User.query.filter(User.email == email).first()

        if user_from_db:
            raise ApiEmailInUseException

    def get_user(
        self,
        id: Optional[UUID] = None,
        username: Optional[str] = None,
        **user_kwargs,
    ) -> User:
        if id:
            user_from_db = User.query.get(id)
        elif username:
            user_from_db = User.query.filter_by(username=username, **user_kwargs).first()

        if not user_from_db:
            raise ApiUserNotFoundException

        return user_from_db

    def get_user_history(self, user_id: UUID) -> list[LoginHistory]:
        """Получить данные из login_history по ключу user_id."""

        return LoginHistory.query.filter(LoginHistory.user_id == user_id).all()

    def store_user_login_history(self, user_id: UUID, info: str) -> None:
        history = LoginHistory(user_id=user_id, info=info)
        db.session.add(history)
        db.session.commit()

        return None

    def set_user_role(self, role_name: str, user_name: str):
        role = db.session.query(Role).filter(Role.name == role_name).first()

        if not role:
            raise exc.ApiRoleNotFoundException

        user = db.session.query(User).filter(User.username == user_name).first()

        if not user:
            raise exc.ApiUserNotFoundException

        user.roles.append(role)
        db.session.add(user)
        db.session.commit()

    def set_role_to_user(self, user: User, role: Role) -> None:
        user.roles.append(role)
        db.session.commit()

        return None

    def delete_user_role(self, user: User, role: Role) -> None:
        user.roles.remove(role)
        db.session.commit()

        return None
