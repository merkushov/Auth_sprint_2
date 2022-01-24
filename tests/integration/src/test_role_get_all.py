from http import HTTPStatus as status

from flask import Response
import pytest

from models.db.auth_model import Role


@pytest.mark.usefixtures("clear_cache")
class TestGetRoles:
    url = "/api/v1/role"
    role = {"name": "test_role_name"}

    def test_success(self, client, auth_request, session):
        """Успешный запрос."""
        session.add(Role(name="name_1"))
        session.add(Role(name="name_2"))
        session.add(Role(name="name_3"))
        session.commit()

        resp: Response = client.get(self.url, **auth_request)

        roles_data = resp.get_json()

        assert resp.status_code == status.OK
        assert len(roles_data) == 3
        assert roles_data[0]["name"] == "name_1"
        assert roles_data[1]["name"] == "name_2"
        assert roles_data[2]["name"] == "name_3"

    def test_empty_roles(self, client, auth_request):
        """Случай, когда ролей в БД нет."""
        resp: Response = client.get(self.url, **auth_request)

        roles_data = resp.get_json()

        assert resp.status_code == status.OK
        assert len(roles_data) == 0
