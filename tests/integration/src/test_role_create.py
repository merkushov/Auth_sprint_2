import json
from http import HTTPStatus as status

from flask import Response
import pytest

from models.db.auth_model import Role


@pytest.mark.usefixtures("clear_cache")
class TestCreateRole:
    url = "/api/v1/role"
    role = {"name": "test_role_name"}

    def test_success(self, client, auth_request):
        """Протестировать создание Роли."""

        resp: Response = client.post(
            self.url, data=json.dumps(self.role), **auth_request
        )

        role_data = resp.get_json()

        assert resp.status_code == status.CREATED
        assert role_data.get("id", None) is not None
        assert role_data["name"] == self.role["name"]

    def test_db_state(self, client, auth_request, session):
        """Протестировать изменение состояния БД."""
        db_role = session.query(Role).filter(Role.name == self.role["name"]).first()
        assert db_role is None

        client.post(self.url, data=json.dumps(self.role), **auth_request)

        db_role = session.query(Role).filter(Role.name == self.role["name"]).first()
        assert db_role.name == self.role["name"]

    def test_params_id(self, client, auth_request):
        """Проверка входных параметров: id - не должно передаваться снаружи."""

        custom_role = {
            "id": "a392d2fd-2682-40d9-8de9-013e172e6bb4",
            "name": "request_with_id",
        }
        resp: Response = client.post(
            self.url, data=json.dumps(custom_role), **auth_request
        )

        role_data = resp.get_json()

        assert resp.status_code == status.CREATED
        assert role_data["id"] != custom_role["id"]

    def test_params_required(self, client, auth_request):
        """Проверка входных параметров: name - обязательное поле."""

        resp: Response = client.post(self.url, data=json.dumps({}), **auth_request)

        assert resp.status_code == status.UNPROCESSABLE_ENTITY

    def test_insert_twice(self, client, auth_request):
        """Повторная вставка Роли с одинаковым именем не допускается."""
        client.post(self.url, data=json.dumps(self.role), **auth_request)
        resp: Response = client.post(
            self.url, data=json.dumps(self.role), **auth_request
        )

        assert resp.status_code == status.CONFLICT
