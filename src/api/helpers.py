from functools import wraps

from flask import Request, request

import exceptions as exc
from config import app_config
from models.api.tokens import AccessToken
from services import JWTService, get_jwt_service


def get_access_token(request: Request) -> str:
    access_token_str = None

    if "Authorization" in request.headers:
        token_header = request.headers["Authorization"].split(" ")
        access_token_str = token_header[-1]

    return access_token_str


def decode_access_token(service: JWTService, encoded_token: str) -> AccessToken:
    return service.decode(encoded_token=encoded_token)


def validate_access_token(service: JWTService, access_token: AccessToken) -> None:
    if access_token.type != app_config.access_token_type:
        raise exc.ApiTokenWrongTypeException

    service.is_expired(token=access_token)
    service.is_in_blacklist(token=access_token)


def auth_required(f):
    """Декоратор, который используется в контроллерах для авторизации. Он
    вытаскивает access-токен из заголовка, расшифровывает его и валидирует. В
    параметрах декорируемой функции можено получить декодированный токен по
    имени "access_token".

    В случае, если токена нет или он не валидный, декоратор возвращает
    различные исключения. Исключения перехватываются на уровне
    фреймворка Flask и формируют ответ, понятный Клиенту.
    """
    jwt_service: JWTService = get_jwt_service()

    @wraps(f)
    def decorator(*args, **kwargs):
        access_token_str = get_access_token(request)

        if not access_token_str:
            raise exc.ApiForbiddenUserException

        access_token = decode_access_token(
            service=jwt_service, encoded_token=access_token_str
        )

        validate_access_token(
            service=jwt_service,
            access_token=access_token,
        )

        return f(*args, access_token, **kwargs)

    return decorator
