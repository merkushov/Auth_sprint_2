import json
from http import HTTPStatus as status

import pytest
from flask import Response

from models.db.auth_model import User


@pytest.mark.usefixtures("clear_cache")
class TestSetRoleToUser:
    url = "/api/v1/user/{user_id}/role/{role_id}"
    role = {"name": "test_role"}

    @pytest.fixture
    def test_role(self, client, auth_request):
        """Создание тестовой роли."""

        resp: Response = client.post(
            "/api/v1/role", data=json.dumps(self.role), **auth_request
        )

        role_data = resp.get_json()

        yield role_data

    def test_success(self, client, test_user, test_role, auth_request):
        """Успешно установить Роль Пользователю."""
        resp: Response = client.post(
            self.url.format(user_id=test_user["id"], role_id=test_role["id"]),
            **auth_request
        )

        assert resp.status_code == status.CREATED

    def test_check_db_state(self, client, test_user, test_role, auth_request, session):
        """Проверяем изменение состояния БД."""
        user = session.query(User).filter(User.id == test_user["id"]).first()
        has_role = False
        for role in user.roles:
            if str(role.id) == test_role["id"]:
                has_role = True
                break
        assert has_role is False

        resp: Response = client.post(
            self.url.format(user_id=test_user["id"], role_id=test_role["id"]),
            **auth_request
        )

        assert resp.status_code == status.CREATED

        user = session.query(User).filter(User.id == test_user["id"]).first()
        has_role = False
        for role in user.roles:
            if str(role.id) == test_role["id"]:
                has_role = True
                break
        assert has_role is True

    def test_insert_twice(self, client, test_user, test_role, auth_request):
        """Попытка вставки одной и той же записи дважды."""

        resp: Response = client.post(
            self.url.format(user_id=test_user["id"], role_id=test_role["id"]),
            **auth_request
        )

        assert resp.status_code == status.CREATED

        resp: Response = client.post(
            self.url.format(user_id=test_user["id"], role_id=test_role["id"]),
            **auth_request
        )

        assert resp.status_code == status.CREATED

    def test_params_wrong_id_format(self, client, test_user, test_role, auth_request):
        """Неверный формат идентификатора."""

        resp: Response = client.post(
            self.url.format(user_id="fake_user", role_id=test_role["id"]),
            **auth_request
        )

        assert resp.status_code == status.UNPROCESSABLE_ENTITY

        resp: Response = client.post(
            self.url.format(user_id=test_user["id"], role_id="fake_role"),
            **auth_request
        )

        assert resp.status_code == status.UNPROCESSABLE_ENTITY

    def test_params_wrong_id(self, client, test_user, test_role, auth_request):
        """Неверный формат идентификатора."""

        resp: Response = client.post(
            self.url.format(
                user_id="a392d2fd-2682-40d9-8de9-013e172e6bb4",
                role_id="a392d2fd-2682-40d9-8de9-013e172e6bb4",
            ),
            **auth_request
        )

        assert resp.status_code == status.NOT_FOUND
