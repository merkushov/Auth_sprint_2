import abc
import logging
from uuid import UUID

import sqlalchemy as sa

import exceptions as exc
from db import db
from models.db.auth_model import Role


class IRoleStorage:
    """Базовый абстрактный класс хранилища данных ролей."""

    @abc.abstractmethod
    def get_roles(self) -> list[Role]:
        """Получить все Роли."""

    @abc.abstractmethod
    def get_role(self, role_id: UUID) -> Role:
        """Получить одну Роль по идентификатору."""

    @abc.abstractmethod
    def create_role(self, raw_data: dict) -> Role:
        """Создать новую Роль."""

    @abc.abstractmethod
    def update_role(self, role_id: UUID, raw_data: dict) -> Role:
        """Обновить существующую Роль по её идентификатору."""

    @abc.abstractmethod
    def delete_role(self, role_id: UUID) -> None:
        """Удалить существующую Роль."""


class PostgresRoleStorage(IRoleStorage):
    def get_roles(self) -> list[Role]:
        """Получить все Роли."""

        roles: list[Role] = Role.query.all()

        return roles

    def get_role(self, role_id: UUID) -> Role:
        """Получить одну Роль по идентификатору."""
        role: Role = Role.query.filter(Role.id == role_id).first()

        if not role:
            raise exc.ApiRoleNotFoundException

        return role

    def create_role(self, raw_data: dict) -> Role:
        """Создать новую Роль."""

        role = Role(**raw_data)
        db.session.add(role)

        try:
            db.session.commit()
        except sa.exc.IntegrityError as exception:
            raise exc.ApiRoleAlreadyExistsException(
                detail=exception.orig.diag.message_detail
            )

        db.session.refresh(role)

        return role

    def update_role(self, role_id: UUID, raw_data: dict) -> Role:
        """Обновить существующую Роль по её идентификатору."""
        stmt = sa.update(Role).filter(Role.id == role_id).values(**raw_data)

        try:
            db.session.execute(stmt)
            db.session.commit()
        except sa.exc.IntegrityError as exception:
            raise exc.ApiRoleNotFoundException(
                detail=exception.orig.diag.message_detail
            )

        role = self.get_role(role_id=role_id)

        return role

    def delete_role(self, role_id: UUID) -> None:
        """Удалить существующую Роль по её идентификатору."""
        deleted_rows = db.session.query(Role).filter(Role.id == role_id).delete()
        db.session.commit()

        if deleted_rows == 0:
            logging.warning(f"Попытка удалить несуществующую Роль '{role_id}'")
            raise exc.ApiRoleNotFoundException

        return None
