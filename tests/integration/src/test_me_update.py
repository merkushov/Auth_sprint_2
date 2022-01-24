import json
from http import HTTPStatus as status

import pytest
from flask import Response

from models.db.auth_model import User


@pytest.mark.usefixtures("clear_cache")
class TestUpdateCurrentUser:
    url = "/api/v1/me"
    original_user = dict(
        username="Test Test", password="Test", email="autotest@yandex.ru"
    )

    @pytest.fixture
    def test_user(self, client) -> dict:
        """Эту фикстуру нужно вставлять в атрибуты метода этого класса, если
        нужно, чтобы перед выполнением был создан новый тестовый
        Пользователь."""
        resp: Response = client.post(
            "/api/v1/user",
            data=json.dumps(self.original_user),
            content_type="application/json",
        )

        yield resp.get_json()

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
                    "username": self.original_user["username"],
                    "password": self.original_user["password"],
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

    def test_update_current_unautorized_access(self, test_user, client):
        """Неавторизованных доступ."""
        user_data = {
            "id": test_user["id"],
            "username": "New username",
        }
        resp: Response = client.put(
            self.url, data=json.dumps(user_data), content_type="application/json"
        )

        assert resp.status_code == status.FORBIDDEN

    def test_update_current_autorized_access(self, test_user, auth_request, client):
        """Неавторизованных доступ."""
        user_data = {
            "id": test_user["id"],
            "username": "New username",
        }
        resp: Response = client.put(
            self.url,
            data=json.dumps(user_data),
            **auth_request,
        )

        assert resp.status_code == status.OK

    def test_update_current_user_db_state(
        self, test_user, auth_request, client, session
    ):
        """Проверяем, что запрос изменил состояние БД."""

        user_data = {
            "id": test_user["id"],
            "username": "New username",
        }
        assert test_user["username"] != user_data["username"]

        resp: Response = client.put(
            self.url, data=json.dumps(user_data), **auth_request
        )

        assert resp.status_code == status.OK

        # Проверка наличия изменений Пользователя в БД
        db_user = session.query(User).filter(User.id == user_data["id"]).first()
        assert db_user.username == user_data["username"]

        # TODO: создать тест Сервиса UserService и вынести эту проверку туда
        assert db_user.password_hash != self.original_user["password"]

    def test_update_current_user_success(self, test_user, auth_request, client):
        """Проверяем что успешный ответ API соответствует ожиданиям."""

        user_data = {
            "id": test_user["id"],
            "username": "New username",
        }
        resp: Response = client.put(
            self.url, data=json.dumps(user_data), **auth_request
        )

        assert resp.status_code == status.OK
        new_user_data = resp.get_json()

        # не должно быть пароля и ролей
        assert new_user_data.get("password", None) is None
        assert new_user_data.get("password_hash", None) is None
        assert new_user_data.get("roles", None) is None

        # эти данные изменились
        assert new_user_data["username"] != test_user["username"]
        assert new_user_data["username"] == user_data["username"]

        # эти данные не изменились
        assert new_user_data["email"] == test_user["email"]

    def test_update_current_user_missing_id(self, test_user, auth_request, client):
        """Невалидный запрос.

        Отсутствует ID
        """

        resp: Response = client.put(
            self.url, data=json.dumps({"username": "Victor"}), **auth_request
        )

        assert resp.status_code == status.UNPROCESSABLE_ENTITY
        new_user_data = resp.get_json()

        assert new_user_data.get("message", None)
        assert new_user_data.get("detail", None)
