from functools import wraps

from flask import request

import exceptions as exc
from config import Config
from models.api.tokens import AccessToken
from services import JWTService, get_jwt_service


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
        access_token_str = None

        # Формат заголовка: "Authorization: Bearer <token_string>"
        if "Authorization" in request.headers:
            token_header = request.headers["Authorization"].split(" ")
            access_token_str = token_header[-1]

        if not access_token_str:
            raise exc.ApiForbiddenUserException

        access_token: AccessToken = jwt_service.decode(encoded_token=access_token_str)

        if access_token.type != Config.ACCESS_TOKEN_TYPE:
            raise exc.ApiTokenWrongTypeException

        jwt_service.is_expired(token=access_token)
        jwt_service.is_in_blacklist(token=access_token)

        return f(*args, access_token, **kwargs)

    return decorator
