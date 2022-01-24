"""Все эндпоинты относящиеся к Авторизованному пользователю."""

from flask import jsonify

from api.helpers import auth_required
from models.api.tokens import AccessToken
from services import UserService, get_user_service


class AccessHistoryController:
    def __init__(
        self,
        user_service: UserService = get_user_service(),
    ):
        self.user_service = user_service

    @auth_required
    def get_access_history(self, access_token: AccessToken):
        """Получить информацию о входах активного Пользователя в систему.

        Отображает время входа и данные об устройстве, с которого был
        выполнен вход.
        """

        user_histsory = self.user_service.get_user_access_history(
            user_id=access_token.user_id
        )

        output_history = [item.dict() for item in user_histsory]

        return jsonify(output_history)
