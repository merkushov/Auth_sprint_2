import json
from http import HTTPStatus as status

import pytest
from flask import Response


@pytest.mark.usefixtures("clear_cache")
class TestLogin:
    """Тестирование обновления refresh-токена."""

    url = "/api/v1/me/refresh_token"
    user = dict(username="Test Test", password="Test")
    user_json = json.dumps(user)

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

    @pytest.fixture
    def tokens(self, client, create_test_user):
        """Совершаем вход пользователя и возвращаем токены."""
        resp: Response = client.post(
            "/api/v1/login", data=self.user_json, content_type="application/json"
        )

        yield resp.get_json()

    def test_refresh_right_token(self, client, session, tokens):
        """Проверяем обновление валидного refresh токена."""
        refresh_token = {"refresh_token": tokens["refresh"]}
        resp: Response = client.put(
            self.url, data=json.dumps(refresh_token), content_type="application/json"
        )

        resp_json = resp.get_json()

        assert resp.status_code == status.OK

        # проверка на наличие JWT ключей в ответе
        assert "access" in resp_json
        assert "refresh" in resp_json

    def test_refresh_right_token_two_times(self, client, tokens):
        """Проверяем обновление валидного refresh токена два раза подряд.

        Вторая попытка обновить refresh токен должна закончиться
        неудачей.
        """
        refresh_token = {"refresh_token": tokens["refresh"]}
        resp: Response = client.put(
            self.url, data=json.dumps(refresh_token), content_type="application/json"
        )

        assert resp.status_code == status.OK

        resp: Response = client.put(
            self.url, data=json.dumps(refresh_token), content_type="application/json"
        )

        assert resp.status_code == status.NOT_FOUND

    def test_refresh_wrong_token(self, client, session, tokens):
        """Проверяем обновление невалидного refresh токена."""
        refresh_token = {"refresh_token": tokens["refresh"][:-1] + "X"}
        resp: Response = client.put(
            self.url, data=json.dumps(refresh_token), content_type="application/json"
        )

        resp_json = resp.get_json()

        assert resp.status_code == status.UNAUTHORIZED

        assert resp_json["message"] == "Токен не валиден"

    def test_refresh_with_access_token(self, client, session, tokens):
        """Проверяем обновление токена если используем access-токен."""
        refresh_token = {"refresh_token": tokens["access"]}
        resp: Response = client.put(
            self.url, data=json.dumps(refresh_token), content_type="application/json"
        )

        assert resp.status_code == status.UNAUTHORIZED

    def test_scam_access_blacklisted_token(self, client, create_test_user, tokens):
        """Попытка мошенничества: попытка войти по устаревшему access-токену.

        После обновления refresh токена access токен тоже должен был
        измениться. Доступ по старому access токену должен быть
        заблокирован.
        """
        refresh_token = {"refresh_token": tokens["refresh"]}
        resp: Response = client.put(
            self.url, data=json.dumps(refresh_token), content_type="application/json"
        )

        assert resp.status_code == status.OK

        user_data = {
            "id": create_test_user["id"],
            "username": "New username",
        }
        access_token = tokens["access"]

        resp: Response = client.put(
            "/api/v1/me",
            data=json.dumps(user_data),
            headers={"Authorization": f"Bearer {access_token}"},
            content_type="application/json",
        )

        assert resp.status_code == status.UNAUTHORIZED
