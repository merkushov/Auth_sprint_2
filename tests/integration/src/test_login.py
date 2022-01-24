import json
from http import HTTPStatus as status

import pytest
from flask import Response

from models.db.auth_model import LoginHistory, User


@pytest.mark.usefixtures("clear_cache")
class TestLogin:
    """Тестирование логина пользователя."""

    url = "/api/v1/login"
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

    def test_login_user(self, client, create_test_user):
        """Проверяем логин пользователя с валидным именем и паролем."""
        resp: Response = client.post(
            self.url, data=self.user_json, content_type="application/json"
        )

        assert resp.status_code == status.OK
        resp_json = resp.get_json()

        # проверка на наличие JWT ключей в ответе
        assert "access" in resp_json
        assert "refresh" in resp_json

    def test_login_missing_user(self, client):
        """Проверяем логин ранее незарегистрированного пользователя."""
        resp: Response = client.post(
            self.url, data=self.user_json, content_type="application/json"
        )

        assert resp.status_code == status.NOT_FOUND
        resp_json = resp.get_json()

        assert resp_json["message"] == "Пользователь не найден в базе данных"

    def test_login_wrong_password(self, client, create_test_user):
        """Проверяем логин c неправильным email или паролем."""
        user_json = json.dumps(dict(username="Test Test", password="wrong_password"))

        resp: Response = client.post(
            self.url, data=user_json, content_type="application/json"
        )

        assert resp.status_code == status.UNPROCESSABLE_ENTITY
        resp_json = resp.get_json()

        assert resp_json["message"] == "Неверное имя пользователя или пароль"

    def test_login_history(self, session, client, create_test_user):
        """Тестирование создания записи в БД о факте логина пользователя."""
        client.post(self.url, data=self.user_json, content_type="application/json")

        user_from_db = (
            session.query(User).filter(User.username == self.user["username"]).first()
        )

        user_history_entry = (
            session.query(LoginHistory)
            .filter(LoginHistory.user_id == user_from_db.id)
            .first()
        )

        assert user_history_entry
