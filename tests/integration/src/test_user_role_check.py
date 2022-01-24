import json
from http import HTTPStatus as status

from flask import Response
import pytest


@pytest.mark.usefixtures("clear_cache")
class TestCheckUserRole:
    url = "/api/v1/user/{user_id}/role/{role_id}"

    def create_role_and_user_role(
        self, client, test_user, auth_request, role_name: str
    ):
        """Создание тестовой роли."""

        resp: Response = client.post(
            "/api/v1/role", data=json.dumps({"name": role_name}), **auth_request
        )

        role_data = resp.get_json()

        client.post(
            self.url.format(user_id=test_user["id"], role_id=role_data["id"]),
            **auth_request
        )

        return role_data

    def test_success(self, client, test_user, auth_request):
        """Успешно проверить Роль Пользователя."""
        test_role = self.create_role_and_user_role(
            client, test_user, auth_request, role_name="test_role"
        )

        resp: Response = client.get(
            self.url.format(user_id=test_user["id"], role_id=test_role["id"]),
            **auth_request
        )

        data = resp.get_json()

        assert resp.status_code == status.OK
        assert data["has_role"] is True

    def test_failure(self, client, test_user, auth_request):
        """Случай, когда Роль не связана с Пользователем."""
        resp: Response = client.post(
            "/api/v1/role", data=json.dumps({"name": "fail_role"}), **auth_request
        )

        role = resp.get_json()

        assert resp.status_code == status.CREATED

        resp: Response = client.get(
            self.url.format(user_id=test_user["id"], role_id=role["id"]), **auth_request
        )

        data = resp.get_json()

        assert resp.status_code == status.OK
        assert data["has_role"] is False

    def test_success_set_of_roles(self, client, test_user, auth_request):
        """Успешно проверить Роль Пользователя из набора ролей."""
        role_1 = self.create_role_and_user_role(
            client, test_user, auth_request, role_name="n1"
        )
        role_2 = self.create_role_and_user_role(
            client, test_user, auth_request, role_name="n2"
        )

        resp: Response = client.get(
            self.url.format(user_id=test_user["id"], role_id=role_1["id"]),
            **auth_request
        )

        data = resp.get_json()

        assert resp.status_code == status.OK
        assert data["has_role"] is True

        resp: Response = client.get(
            self.url.format(user_id=test_user["id"], role_id=role_2["id"]),
            **auth_request
        )

        data = resp.get_json()

        assert resp.status_code == status.OK
        assert data["has_role"] is True

    def test_params_wrong_id_format(self, client, test_user, auth_request):
        """Неверный формат идентификатора."""
        test_role = self.create_role_and_user_role(
            client, test_user, auth_request, role_name="test_role"
        )

        resp: Response = client.get(
            self.url.format(user_id="fake_user", role_id=test_role["id"]),
            **auth_request
        )

        assert resp.status_code == status.UNPROCESSABLE_ENTITY

        resp: Response = client.get(
            self.url.format(user_id=test_user["id"], role_id="fake_role"),
            **auth_request
        )

        assert resp.status_code == status.UNPROCESSABLE_ENTITY

    def test_params_wrong_id(self, client, test_user, auth_request):
        """Неверный формат идентификатора."""
        self.create_role_and_user_role(
            client, test_user, auth_request, role_name="test_role"
        )

        resp: Response = client.get(
            self.url.format(
                user_id="a392d2fd-2682-40d9-8de9-013e172e6bb4",
                role_id="a392d2fd-2682-40d9-8de9-013e172e6bb4",
            ),
            **auth_request
        )

        assert resp.status_code == status.NOT_FOUND
