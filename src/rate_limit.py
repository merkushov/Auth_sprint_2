import hashlib
import logging
from datetime import datetime

from flask import Flask, request
from flask_redis import FlaskRedis

import exceptions as exc
from api.helpers import decode_access_token, get_access_token, validate_access_token
from config import app_config
from services import JWTService, get_jwt_service


def check_limit(redis_client: FlaskRedis, jwt_service: JWTService) -> None:
    key_id = ""

    # TODO: скомбинировать rate_limit и auth_required так, чтобы не приходилось
    #       два раза проверять access_token
    access_token_str = get_access_token(request)
    if access_token_str:
        access_token = decode_access_token(
            service=jwt_service, encoded_token=access_token_str
        )

        validate_access_token(
            service=jwt_service,
            access_token=access_token,
        )

        key_id = f"user_id:{access_token.user_id}"

        annon = False

    if not key_id:
        key_id = hashlib.md5(
            bytes(request.remote_addr + str(request.user_agent), "utf8")
        ).hexdigest()

        annon = True

    key = "rate_limit:{id}:{timestamp}".format(
        id=key_id,
        timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M"),
    )

    pipe = redis_client.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, 59)
    counter, _ = pipe.execute()

    if (
        annon is True
        and counter > app_config.rate_limit_threshold_annon_per_minute
        or annon is False
        and counter > app_config.rate_limit_threshold_registered_per_minute
    ):
        if annon is True:
            excess_amount = counter - app_config.rate_limit_threshold_annon_per_minute
        else:
            excess_amount = (
                counter - app_config.rate_limit_threshold_registered_per_minute
            )

        logging.warning("Request limit exceeded by %s. Key: %s", excess_amount, key)
        raise exc.ApiTooManyRequestsException


def init_rate_limit(app: Flask, redis_client: FlaskRedis) -> None:
    """Инициализировать функционал ограничения количества запросов."""

    jwt_service = get_jwt_service()

    @app.before_request
    def check_rate_limit():
        check_limit(redis_client, jwt_service)

    return None
