import json
from http import HTTPStatus as status

from flask import Response
import pytest

from models.db.auth_model import User


@pytest.mark.usefixtures("clear_cache")
class TestRegisterUser:
    url = "/api/v1/user"
    user = dict(username="Test Test", password="Test", email="autotest@yandex.ru")
    user_json = json.dumps(user)

    def test_register_user_db_state(self, client, session):
        """Проверяем, что запрос изменил состояние БД."""
        resp: Response = client.post(
            self.url, data=self.user_json, content_type="application/json"
        )

        assert resp.status_code == status.CREATED
        new_user_data = resp.get_json()

        # Проверка на наличие нового Пользователя в БД
        assert session.query(User).filter(User.id == new_user_data["id"]).first()

    def test_register_user(self, client):
        """Тестирование эндпоинта регистрации Пользователя в Системе."""
        resp: Response = client.post(
            self.url, data=self.user_json, content_type="application/json"
        )

        json_data = resp.get_json()

        assert resp.status_code == status.CREATED
        assert json_data["id"]
        assert json_data["username"] == self.user["username"]
        assert json_data["email"] == self.user["email"]
        assert json_data.get("password", None) is None

    def test_register_user_duplicate(self, client):
        """Попытка повторно создать такого же Пользователя."""

        resp_first: Response = client.post(
            self.url, data=self.user_json, content_type="application/json"
        )

        assert resp_first.status_code == status.CREATED

        resp_second: Response = client.post(
            self.url, data=self.user_json, content_type="application/json"
        )

        assert resp_second.status_code == status.CONFLICT

    def test_register_user_wrong_email(self, client):
        """Валидация параметров.

        Неверный email
        """
        resp: Response = client.post(
            "/api/v1/user",
            data=json.dumps(
                {"username": "Test", "password": "Test", "email": "test@localhost"}
            ),
            content_type="application/json",
        )

        assert resp.status_code == status.UNPROCESSABLE_ENTITY
