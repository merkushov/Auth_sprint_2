from http import HTTPStatus as status

from flask import Response


def test_ping(client):
    """Тестирование пинговалки сервиса."""
    resp: Response = client.get("/api/v1/ping")
    json_data = resp.get_json()

    assert resp.status_code == status.OK
    assert json_data["ping"] == "pong"
