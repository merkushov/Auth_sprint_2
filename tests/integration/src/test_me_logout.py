import json
from http import HTTPStatus as status

import pytest
from flask import Response

from redis_client import redis_client
from services import get_jwt_service


@pytest.mark.usefixtures("clear_cache")
class TestLogout:
    """Тестирование разлогина пользователя."""

    url = "/api/v1/me/logout"
    user = dict(username="Test Test", password="Test")
    user_json = json.dumps(user)

    @pytest.fixture
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

        yield dict(
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

    def test_logout(self, client, create_test_user, auth_request):
        """Проверяем логаут пользователя."""
        auth_data = auth_request

        resp: Response = client.get(
            self.url,
            data=self.user_json,
            **auth_data,
        )

        acces_token = auth_data["headers"]["Authorization"].split()[1]
        access_token_jti = get_jwt_service().decode(acces_token).jti

        assert redis_client.get(f"black_list.access_token.{access_token_jti}")

        assert resp.status_code == status.OK

    def test_logout_without_token(self, client, create_test_user):
        """Проверяем логаут пользователя без access токена."""

        resp: Response = client.get(
            self.url,
            data=self.user_json,
        )

        assert resp.status_code == status.FORBIDDEN
        assert resp.get_json()["message"] == "Не хватает прав"

    def test_wrong_token_logout(self, client, create_test_user, auth_request):
        """Проверяем логаут пользователя c невалидным токеном."""

        auth_data = auth_request
        auth_data["headers"]["Authorization"] = (
            auth_data["headers"]["Authorization"][:-1] + "X"
        )

        resp: Response = client.get(
            self.url,
            data=self.user_json,
            **auth_data,
        )

        assert resp.status_code == status.UNAUTHORIZED
        assert resp.get_json()["message"] == "Токен не валиден"
