import json
import re
from http import HTTPStatus as status

import pytest
from flask import Response

from models.db.auth_model import LoginHistory


@pytest.mark.usefixtures("clear_cache")
class TestUserAccessHistory:
    url = "/api/v1/me/access_history"
    original_user = dict(
        username="User Name",
        password="nai(3b&l3lkas)k3awkB_jd",
        email="autotest_me@yandex.ru",
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

    def test_update_current_user_db_state(self, test_user, client, session):
        """Проверяем, что запрос изменил состояние БД."""

        # без логина данные по пользователю отсутствуют
        history = (
            session.query(LoginHistory)
            .filter(LoginHistory.user_id == test_user["id"])
            .all()
        )
        assert len(history) == 0

        login_request = dict(
            data=json.dumps(
                {
                    "username": self.original_user["username"],
                    "password": self.original_user["password"],
                }
            ),
            content_type="application/json",
        )

        client.post(
            "/api/v1/login",
            **login_request,
            headers={"User-Agent": "my_test_agent"},
        )
        client.post(
            "/api/v1/login",
            **login_request,
            headers={"User-Agent": "my_another_test_agent"},
        )
        client.post(
            "/api/v1/login",
            **login_request,
            # Default User-Agent: werkzeug/2.0.2
        )

        history = (
            session.query(LoginHistory)
            .filter(LoginHistory.user_id == test_user["id"])
            .order_by(LoginHistory.created_at)
            .all()
        )

        assert len(history) == 3
        assert re.match("my_test_agent", history[0].info)
        assert re.match("my_another_test_agent", history[1].info)
        assert re.match("werkzeug", history[2].info)

    def test_access_history_success(self, client, test_user, auth_request):
        resp: Response = client.get(self.url, **auth_request)

        history = resp.get_json()

        assert resp.status_code == status.OK
        assert len(history) == 1
        assert history[0].get("user_agent", None) is not None
        assert history[0].get("datetime", None) is not None
