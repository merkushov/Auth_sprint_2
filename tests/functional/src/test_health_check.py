from http import HTTPStatus
from typing import Callable

import pytest


@pytest.mark.asyncio
async def test_health_check(make_get_request: Callable):
    response = await make_get_request("/ping")

    assert response.status == HTTPStatus.OK
    assert response.body["ping"] == "pong"
