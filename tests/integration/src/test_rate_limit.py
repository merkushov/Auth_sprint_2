import json
from http import HTTPStatus as status
from config import app_config

from flask import Response
import pytest

# from models.db.auth_model import User

# TODO: тест мигающий! Подумать, как уложться в минутные лимиты

@pytest.mark.usefixtures("clear_cache")
class TestUserRateLimit:

    def test_user_limit(self, app, client, auth_request):
        """Проверить лимиты авторизованного пользователя."""
        url = "/api/v1/user/{user_id}/role/{role_id}".format(
            user_id="a392d2fd-2682-40d9-8de9-013e172e6bb4",
            role_id="a392d2fd-2682-40d9-8de9-013e172e6bb4",
        )

        for i in range(app_config.rate_limit_threshold_registered_per_minute):
            resp: Response = client.get(url, **auth_request)

            assert resp.status_code == status.NOT_FOUND

        resp: Response = client.get(url, **auth_request)

        assert resp.status_code == status.TOO_MANY_REQUESTS


@pytest.mark.usefixtures("clear_cache")
class TestAnnonRateLimit:
    def test_annon_limit(self, app, client):
        """Проверяем лимиты неавторизованного пользователя."""
        url = "/api/v1/login"
        user = dict(username="Rate Limit", password="dInd34#jg(jlasxkd")
        user_json = json.dumps(user)

        for _ in range(app_config.rate_limit_threshold_annon_per_minute):
            resp: Response = client.post(
                url, data=user_json, content_type="application/json"
            )

            assert resp.status_code == status.NOT_FOUND

        resp: Response = client.post(
            url, data=user_json, content_type="application/json"
        )
        assert resp.status_code == status.TOO_MANY_REQUESTS