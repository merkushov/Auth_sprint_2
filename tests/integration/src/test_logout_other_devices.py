import json
from http import HTTPStatus as status
from uuid import UUID

import pytest
from flask import Response

from models.db.auth_model import RefreshJwt
from services import get_jwt_service


@pytest.mark.usefixtures("clear_cache")
class TestLogoutOtherDevices:
    """Тестирование разлогина пользователя из других активных сессий."""

    url = "/api/v1/me/logout_other_devices"
    user = dict(username="Test Test", password="Test")
    user_json = json.dumps(user)

    def auth_request(self, client) -> dict:
        """Авторизация тестового пользователя.

        Метод возвращает словарь, содержащий параметры (заголовки и тип
        контента) необходимые для выполнения успешного авторизованного
        запроса.
        """

        resp: Response = client.post(
            "/api/v1/login",
            data=json.dumps(
                {
                    "username": self.user["username"],
                    "password": self.user["password"],
                }
            ),
            content_type="application/json",
        )

        token_pair = resp.get_json()
        access_token = token_pair["access"]

        return dict(
            headers={"Authorization": f"Bearer {access_token}"},
            content_type="application/json",
        )

    @pytest.fixture
    def create_test_user(self, client) -> dict:
        """Эту фикстуру нужно вставлять в атрибуты метода этого класса, если
        нужно, чтобы перед выполнением был создан новый тестовый
        Пользователь."""

        resp: Response = client.post(
            "/api/v1/user",
            data=json.dumps({**self.user, **{"email": "test@test.com"}}),
            content_type="application/json",
        )

        yield resp.get_json()

    def test_logout_other_devices(self, client, create_test_user, session):
        """Проверяем логаут пользователя из других сессий кроме текущей."""

        auth_data = self.auth_request(client)

        # логинимся еще два раза
        self.auth_request(client)
        self.auth_request(client)

        acces_token = auth_data["headers"]["Authorization"].split()[1]
        user_id = get_jwt_service().decode(acces_token).user_id

        refresh_jwts_from_db = (
            session.query(RefreshJwt).filter(RefreshJwt.user_id == UUID(user_id)).all()
        )

        # до разлогина было 3 записи
        assert len(refresh_jwts_from_db) == 3

        resp: Response = client.get(
            self.url,
            data=self.user_json,
            **auth_data,
        )

        refresh_jwts_from_db = (
            session.query(RefreshJwt).filter(RefreshJwt.user_id == UUID(user_id)).all()
        )

        # осталась одна запись
        assert len(refresh_jwts_from_db) == 1

        assert resp.status_code == status.OK

        # TODO: получить access-токены после остальных логинов и попробовать
        # доступ по ним
