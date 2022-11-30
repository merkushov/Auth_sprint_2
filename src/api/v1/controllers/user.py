"""Контроллер обслуживающий функционал Пользователь-Роль."""
import logging
from http import HTTPStatus as status
from uuid import UUID

from flask import jsonify, request

import exceptions as exc
from api.helpers import auth_required
from models.api.tokens import AccessToken
from models.api.user import InputUpdateUser, InputUserRole, OutputUser, User
from services import UserService, get_user_service


class UserController:
    def __init__(self, user_service: UserService = get_user_service()):
        self.user_service = user_service

    @auth_required
    def set_role_to_user(self, access_token: AccessToken, user_id: UUID, role_id: UUID):
        """Задать Роль Пользователю."""

        # валидация входных параметров
        InputUserRole(user_id=user_id, role_id=role_id)

        self.user_service.set_role_to_user(user_id=user_id, role_id=role_id)

        return jsonify({}), status.CREATED

    @auth_required
    def check_user_role(self, access_token: AccessToken, user_id: UUID, role_id: UUID):
        """Проверить наличие Роли у Пользователя."""

        # валидация входных параметров
        InputUserRole(user_id=user_id, role_id=role_id)

        has_role = self.user_service.check_user_role(user_id=user_id, role_id=role_id)
        if has_role:
            response_data = {"has_role": True}
        else:
            response_data = {"has_role": False}

        return jsonify(response_data), status.OK

    @auth_required
    def get_my_roles(self, access_token: AccessToken):
        """Возвращает все роли текущего пользователя"""

        user = self.user_service.get_user(id=access_token.user_id)
        output_roles = [role.dict() for role in user.roles]

        return jsonify(output_roles), status.OK

    @auth_required
    def delete_user_role(self, access_token: AccessToken, user_id: UUID, role_id: UUID):
        """Удалить Роль у Пользователя."""

        # валидация входных параметров
        InputUserRole(user_id=user_id, role_id=role_id)

        self.user_service.delete_user_role(user_id=user_id, role_id=role_id)

        return {}, status.NO_CONTENT

    @auth_required
    def update_current_user(self, access_token: AccessToken):
        """Обновить данные Пользователя."""

        # Получить входные данные
        user = InputUpdateUser.parse_obj(request.json)

        if str(user.id) != str(access_token.user_id):
            logging.error(f"Request user: {user.id} Token user: {access_token.user_id}")
            raise exc.ApiForbiddenUserException(
                detail="Запрещено редактировать другого Пользователя"
            )

        updated_user: User = self.user_service.update_user(user)

        output_user = OutputUser(**updated_user.dict())

        return jsonify(output_user.dict()), status.OK

    @auth_required
    def get_current_user_info(self, access_token: AccessToken):
        """Возвращает информацию по авторизованному пользователю"""

        user = self.user_service.get_user(id=access_token.user_id)

        output_user = OutputUser(**user.dict())

        return jsonify(output_user.dict()), status.OK
