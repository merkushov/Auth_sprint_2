import json
from http import HTTPStatus as status

from flask import Response
import pytest

from models.db.auth_model import Role


@pytest.mark.usefixtures("clear_cache")
class TestUpdateRole:
    url = "/api/v1/role/{role_id}"
    role = {"name": "test_role_name"}
    new_name = "role_new_name_2"

    def create_role(self, session, name: str):
        role = Role(name=name)
        session.add(role)
        session.commit()

        return role

    def test_update_success(self, client, auth_request, session):
        """Тестирование успешного обновления Роли."""
        role = self.create_role(session, self.role["name"])

        resp: Response = client.put(
            self.url.format(role_id=role.id),
            data=json.dumps({"name": self.new_name}),
            **auth_request
        )

        role_data = resp.get_json()

        assert resp.status_code == status.OK
        assert role_data["name"] == self.new_name

    def test_params_invalid_role_id(self, client, auth_request, session):
        """Валидация входного параметра: невалидный UUID."""
        self.create_role(session, self.role["name"])

        resp: Response = client.put(
            self.url.format(role_id="fake"),
            data=json.dumps({"name": self.new_name}),
            **auth_request
        )

        assert resp.status_code == status.UNPROCESSABLE_ENTITY

    def test_params_required_name(self, client, auth_request, session):
        """Валидация входного параметра: обязательное имя роли."""
        role = self.create_role(session, self.role["name"])

        resp: Response = client.put(
            self.url.format(role_id=role.id),
            data=json.dumps({"name": ""}),
            **auth_request
        )

        assert resp.status_code == status.UNPROCESSABLE_ENTITY

    def test_params_fake_role_id(self, client, auth_request):
        """Валидация входного параметра: фейковый идентификатор роли."""
        resp: Response = client.put(
            self.url.format(role_id="b658dcc4-a3a9-43bd-ae13-b31b57d43dd0"),
            data=json.dumps({"name": self.new_name}),
            **auth_request
        )

        assert resp.status_code == status.NOT_FOUND

    def test_params_change_id(self, client, auth_request, session):
        """Попытка сменить ID Роли."""
        role = self.create_role(session, self.role["name"])

        new_id = "b658dcc4-a3a9-43bd-ae13-b31b57d43dd0"

        resp: Response = client.put(
            self.url.format(role_id=role.id),
            data=json.dumps({"id": new_id, "name": self.new_name}),
            **auth_request
        )

        role_data = resp.get_json()

        assert resp.status_code == status.OK
        assert role_data["id"] != new_id
        assert role_data["name"] == self.new_name
