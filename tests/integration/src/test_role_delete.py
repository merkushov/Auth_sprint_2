from http import HTTPStatus as status

from flask import Response
import pytest

from models.db.auth_model import Role


@pytest.mark.usefixtures("clear_cache")
class TestDeleteRole:
    url = "/api/v1/role/{role_id}"
    role = {"name": "test_role_name"}
    new_name = "role_new_name_2"

    def create_role(self, session, name: str):
        role = Role(name=name)
        session.add(role)
        session.commit()

        return role

    def test_success(self, client, auth_request, session):
        """Тестирование успешного обновления Роли."""
        role = self.create_role(session, self.role["name"])

        resp: Response = client.delete(self.url.format(role_id=role.id), **auth_request)

        assert resp.status_code == status.NO_CONTENT

    def test_db_status(self, client, auth_request, session):
        """Проверка изменения состояния БД."""
        role = self.create_role(session, self.role["name"])

        resp: Response = client.delete(self.url.format(role_id=role.id), **auth_request)

        assert resp.status_code == status.NO_CONTENT

        db_role = session.query(Role).filter(Role.id == role.id).first()
        assert db_role is None

    def test_params_invalid_role_id(self, client, auth_request, session):
        """Валидация входного параметра: невалидный UUID."""
        self.create_role(session, self.role["name"])

        resp: Response = client.delete(self.url.format(role_id="fake"), **auth_request)

        assert resp.status_code == status.UNPROCESSABLE_ENTITY

    def test_params_fake_role_id(self, client, auth_request):
        """Валидация входного параметра: фейковый идентификатор роли."""
        resp: Response = client.delete(
            self.url.format(role_id="b658dcc4-a3a9-43bd-ae13-b31b57d43dd0"),
            **auth_request
        )

        assert resp.status_code == status.NOT_FOUND
