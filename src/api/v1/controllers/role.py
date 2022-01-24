"""Контроллер обслуживающий Роли."""

from http import HTTPStatus as status
from uuid import UUID

from flask import jsonify, request

from api.helpers import auth_required
from models.api.role import InputRole, InputRoleID, Role
from models.api.tokens import AccessToken
from services import RoleService, get_role_service


class RoleController:
    def __init__(self, role_service: RoleService = get_role_service()):
        self.role_service = role_service

    @auth_required
    def get_roles(self, access_token: AccessToken):
        """Отобразить список всех доступных Ролей в системе."""

        roles = self.role_service.all()

        output_roles = [role.dict() for role in roles]

        return jsonify(output_roles), status.OK

    @auth_required
    def get_role(self, access_token: AccessToken, role_id: UUID):
        """Отобразить Роль по её идентификатору."""

        input_params = InputRoleID(id=role_id)
        role = self.role_service.get(role_id=input_params.id)

        return jsonify(role.dict()), status.OK

    @auth_required
    def create_role(self, access_token: AccessToken):
        """Создать новую Роль."""

        role = InputRole.parse_obj(request.json)

        created_role = self.role_service.create(role=Role(name=role.name))

        return jsonify(created_role.dict()), status.CREATED

    @auth_required
    def update_role(self, access_token: AccessToken, role_id: UUID):
        """Обновить существующую Роль по её идентификатору."""

        # ID - роли берём из url'а и валидируем
        # остальный данные из тела запроса
        input_params = InputRoleID(id=role_id)
        role = InputRole.parse_obj(request.json)

        updated_role = self.role_service.update(
            role=Role(id=input_params.id, name=role.name)
        )

        return jsonify(updated_role.dict()), status.OK

    @auth_required
    def delete_role(self, access_token: AccessToken, role_id: UUID):
        """Удалить существующую Роль по её идентификатору."""

        # валидация входного параметра
        input_params = InputRoleID(id=role_id)

        self.role_service.delete(role_id=input_params.id)

        return jsonify({}), status.NO_CONTENT
