"""Этот модуль содержит все кастомные исключения проекта."""

from typing import Optional


class ApiException(Exception):
    """Базовое исключение для всего Проекта."""

    http_status_code = 500
    message = "Generic error"

    def __init__(
        self,
        message: Optional[str] = None,
        detail: Optional[str] = None,
        payload: Optional[dict] = None,
    ):
        super().__init__()

        if message:
            self.message = message
        else:
            self.message = self.message

        self.detail = detail
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        rv["detail"] = self.detail
        return rv


class ApiInvalidParamsException(ApiException):
    http_status_code = 422


class ApiConflictException(ApiException):
    http_status_code = 409


class ApiNotFoundException(ApiException):
    http_status_code = 404


class ApiForbiddenException(ApiException):
    http_status_code = 403


class ApiUnauthorizedException(ApiException):
    http_status_code = 401


#
# Авторизация Пользователя
#


class ApiValidationErrorException(ApiInvalidParamsException):
    message = "Ошибка валидации"


class ApiLoginInvalidParamsException(ApiInvalidParamsException):
    message = "Неверное имя пользователя или пароль"


#
# Регистрация Пользователя
#


class ApiLoginInUseException(ApiConflictException):
    message = "Имя пользователя уже занято"


class ApiEmailInUseException(ApiConflictException):
    message = "Email уже занят"


class ApiUserAlreadyExistsException(ApiConflictException):
    message = "Пользователь с таким именем или email'ом уже существует"


#
# Обновление access-токена
#


class ApiTokenValidationException(ApiUnauthorizedException):
    message = "Токен не валиден"


class ApiTokenNotFoundException(ApiNotFoundException):
    message = "Токен не найден"


class ApiTokenWrongTypeException(ApiUnauthorizedException):
    message = "Неверный тип токена"


#
# Пользователь
#


class ApiUserNotFoundException(ApiNotFoundException):
    message = "Пользователь не найден в базе данных"


class ApiUserValidationException(ApiInvalidParamsException):
    message = "Ошибка валидации"


class ApiForbiddenUserException(ApiForbiddenException):
    message = "Не хватает прав"


#
# Роли
#


class ApiRoleNotFoundException(ApiNotFoundException):
    message = "Роль не найдена"


class ApiRoleAlreadyExistsException(ApiConflictException):
    message = "Роль с таким именем уже существует"


class ApiRoleValidationException(ApiInvalidParamsException):
    message = "Ошибка валидации"


#
# Пользователь-Роль
#


class ApiUserRoleValidationException(ApiInvalidParamsException):
    message = "Ошибка валидации Пользователя или Роли"


#
# Rate limit
#


class ApiTooManyRequestsException(ApiException):
    http_status_code = 429
    message = "Превышен лимит количества запросов"

#
# Social Account
#


class ApiSocialAccountValidationException(ApiInvalidParamsException):
    message = "Ошибка валидации социального аккаунта"
