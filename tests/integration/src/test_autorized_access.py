import json
from http import HTTPStatus as status

import pytest

from flask import Response

# TODO: Эти кейсы можно описать проще.
#       Отрефакторить, если будет время


@pytest.mark.usefixtures("clear_cache")
def test_authorized_access(client):
    original_user = dict(
        username="Test Test Test",
        password="ajUeknvpq8N3-28cNPZnc;20*djacn",
        email="autotest@yandex.ru",
    )

    client.post(
        "/api/v1/user",
        data=json.dumps(original_user),
        content_type="application/json",
    )

    resp: Response = client.post(
        "/api/v1/login",
        data=json.dumps(
            {
                "username": original_user["username"],
                "password": original_user["password"],
            }
        ),
        content_type="application/json",
    )

    token_pair = resp.get_json()
    access_token = token_pair["access"]

    anon_request = dict(
        content_type="application/json",
    )

    auth_request = dict(
        content_type="application/json",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert client.put("/api/v1/me", **anon_request).status_code == status.FORBIDDEN
    assert client.put("/api/v1/me", **auth_request).status_code != status.FORBIDDEN

    assert (
        client.get("/api/v1/me/access_history", **anon_request).status_code
        == status.FORBIDDEN
    )
    assert (
        client.get("/api/v1/me/access_history", **auth_request).status_code
        != status.FORBIDDEN
    )

    assert client.post("/api/v1/role", **anon_request).status_code == status.FORBIDDEN
    assert client.post("/api/v1/role", **auth_request).status_code != status.FORBIDDEN

    assert client.get("/api/v1/role", **anon_request).status_code == status.FORBIDDEN
    assert client.get("/api/v1/role", **auth_request).status_code != status.FORBIDDEN

    assert (
        client.get("/api/v1/role/fake_role_id", **anon_request).status_code
        == status.FORBIDDEN
    )
    assert (
        client.get("/api/v1/role/fake_role_id", **auth_request).status_code
        != status.FORBIDDEN
    )

    assert (
        client.put("/api/v1/role/fake_role_id", **anon_request).status_code
        == status.FORBIDDEN
    )
    assert (
        client.put("/api/v1/role/fake_role_id", **auth_request).status_code
        != status.FORBIDDEN
    )

    assert (
        client.delete("/api/v1/role/fake_role_id", **anon_request).status_code
        == status.FORBIDDEN
    )
    assert (
        client.delete("/api/v1/role/fake_role_id", **auth_request).status_code
        != status.FORBIDDEN
    )


def test_unauthorized_access(client):
    anon_request = dict(
        content_type="application/json",
    )

    assert client.post("/api/v1/login", **anon_request).status_code != status.FORBIDDEN
    assert client.post("/api/v1/user", **anon_request).status_code != status.FORBIDDEN
    assert (
        client.put("/api/v1/me/refresh_token", **anon_request).status_code
        != status.FORBIDDEN
    )
