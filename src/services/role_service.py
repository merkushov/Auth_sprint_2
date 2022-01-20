from uuid import UUID

from models.api.role import Role
from storage.role_storage import IRoleStorage


class RoleService:
    """Класс сервиса Роли.

    Содержит общий код, для работы с сущностью Роль.
    """

    def __init__(
        self,
        role_storage: IRoleStorage,
    ):
        self.role_storage = role_storage

    def all(self) -> list[Role]:
        """Возвращает все Роли системы."""
        db_roles = self.role_storage.get_roles()

        return [Role.from_orm(db_role) for db_role in db_roles]

    def get(self, role_id: UUID) -> Role:
        """Возвращает Роль по её идентификатору."""
        db_role = self.role_storage.get_role(role_id=role_id)

        return Role.from_orm(db_role)

    def create(self, role: Role) -> Role:
        """Создать новую Роль."""
        db_role = self.role_storage.create_role(role.dict())

        return Role.from_orm(db_role)

    def update(self, role: Role) -> Role:
        """Обновить существующую Роль."""
        db_role = self.role_storage.update_role(
            role_id=role.id, raw_data=dict(name=role.name)
        )

        return Role.from_orm(db_role)

    def delete(self, role_id: UUID) -> None:
        """Удалить существующую Роль."""
        self.role_storage.delete_role(role_id=role_id)

        return None
