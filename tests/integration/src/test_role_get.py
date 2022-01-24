from http import HTTPStatus as status

from flask import Response
import pytest

from models.db.auth_model import Role


@pytest.mark.usefixtures("clear_cache")
class TestGetRole:
    url = "/api/v1/role/{role_id}"
    role = {"name": "test_role_name"}

    def create_role(self, session, name: str):
        role = Role(name=name)
        session.add(role)
        session.commit()

        return role

    def test_success(self, client, auth_request, session):
        """Успешный запрос."""
        role = self.create_role(session, self.role["name"])

        resp: Response = client.get(self.url.format(role_id=role.id), **auth_request)

        roles_data = resp.get_json()

        assert resp.status_code == status.OK
        assert roles_data["id"] == str(role.id)
        assert roles_data["name"] == role.name

    def test_params_invalid_role_id(self, client, auth_request, session):
        """Валидация входного параметра: невалидный UUID."""
        self.create_role(session, self.role["name"])

        resp: Response = client.get(self.url.format(role_id="fake"), **auth_request)

        assert resp.status_code == status.UNPROCESSABLE_ENTITY

    def test_params_fake_role_id(self, client, auth_request, session):
        """Валидация входного параметра: фейковый идентификатор роли."""

        resp: Response = client.get(
            self.url.format(role_id="b658dcc4-a3a9-43bd-ae13-b31b57d43dd0"),
            **auth_request
        )

        assert resp.status_code == status.NOT_FOUND
