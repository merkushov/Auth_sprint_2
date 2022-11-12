import abc
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import and_

import exceptions as exc
from db import db
from exceptions import (
    ApiEmailInUseException,
    ApiLoginInUseException,
    ApiUserAlreadyExistsException,
    ApiUserNotFoundException,
)
from models.db.auth_model import LoginHistory, Role, SocialAccount, User
from telemetry import trace_export


class IUserStorage:
    """Базовый абстрактный класс хранилища данных о пользователе."""

    @abc.abstractmethod
    def get_user(
        self, **user_kwargs
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

    @abc.abstractmethod
    def get_user_by_social_id(self, *args, **kwargs):
        """Получить пользователя по данным социального сервиса."""


class PostgresUserStorage(IUserStorage):
    @trace_export('db_create_user')
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

    @trace_export('db_update_user')
    def update_user(self, id: UUID, raw_data: dict) -> User:
        stmt = sa.update(User).filter(User.id == id).values(**raw_data)

        try:
            db.session.execute(stmt)
            db.session.commit()
        except sa.exc.IntegrityError as exception:
            raise ApiUserNotFoundException(detail=exception.orig.diag.message_detail)

        user = self.get_user(id=id)

        return user

    @trace_export('db_validate_user')
    def _user_credentials_validation(self, username: str, email: str) -> None:
        existed_user = self.get_user(username=username)

        if existed_user:
            raise ApiLoginInUseException

        user_from_db = User.query.filter(User.email == email).first()

        if user_from_db:
            raise ApiEmailInUseException

    @trace_export('get_user')
    def get_user(
        self,
        id: Optional[UUID] = None,
        username: Optional[str] = None,
        **user_kwargs,
    ) -> User:

        if id:
            user_from_db = User.query.get(id)
        elif email := user_kwargs.get('email'):
            user_from_db = User.query.filter_by(email=email).first()
        elif username:
            user_from_db = User.query.filter_by(username=username).first()
        elif user_kwargs:
            user_from_db = User.query.filter_by(**user_kwargs).first()
        else:
            user_from_db = None

        if not user_from_db:
            raise ApiUserNotFoundException

        return user_from_db

    @trace_export('get_user_by_social_id')
    def get_user_by_social_id(self, social_name, social_id):
        user = db.session.query(
            User
        ).join(
            SocialAccount, SocialAccount.user_id == User.id
        ).where(
            and_(SocialAccount.social_name == social_name, SocialAccount.social_id == social_id)
        ).one_or_none()

        if not user:
            raise ApiUserNotFoundException

        return user

    @trace_export('get_user_history')
    def get_user_history(self, user_id: UUID) -> list[LoginHistory]:
        """Получить данные из login_history по ключу user_id."""

        return LoginHistory.query.filter(LoginHistory.user_id == user_id).all()

    def store_user_login_history(self, user_id: UUID, info: str) -> None:
        history = LoginHistory(user_id=user_id, info=info)
        db.session.add(history)
        db.session.commit()

        return None

    @trace_export('set_user_role')
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

    @trace_export('add_user_role')
    def set_role_to_user(self, user: User, role: Role) -> None:
        user.roles.append(role)
        db.session.commit()

        return None

    @trace_export('del_user_role')
    def delete_user_role(self, user: User, role: Role) -> None:
        user.roles.remove(role)
        db.session.commit()

        return None
