import datetime
from typing import List, Union
from uuid import UUID, uuid4

import jwt
import orjson

import exceptions as exc
from config import app_config
from models.api.tokens import AccessToken, RefreshToken, TokenPair
from models.api.user import User
from storage import IJwtStorage
from storage.black_list import IBlackListStorage


class JWTService:
    def __init__(
        self,
        jwt_storage: IJwtStorage,
        black_list_storage: IBlackListStorage,
    ):
        self.jwt_storage = jwt_storage
        self._black_list_storage = black_list_storage

    def create_token_pair(self, user: User) -> TokenPair:
        """Создать и вернуть access и refresh токены."""
        jti: UUID = uuid4()

        access_token = AccessToken(
            jti=str(jti),
            user_id=str(user.id),
            user_roles=[role.name for role in user.roles],
            expired=self._get_token_expiration_time(app_config.access_token_lifetime),
        )
        access_token._encoded_token = self.encode(access_token)

        refresh_token = RefreshToken(
            jti=str(jti),
            user_id=str(user.id),
            expired=self._get_token_expiration_time(app_config.refresh_token_lifetime),
        )
        refresh_token._encoded_token = self.encode(refresh_token)

        token_pair = TokenPair(access=access_token, refresh=refresh_token)
        token_pair._jti = jti

        return token_pair

    def encode(self, token: Union[AccessToken, RefreshToken]) -> str:
        """Закодировать объект Токен в строку JWT формата."""
        return jwt.encode(
            orjson.loads(token.json()),
            app_config.jwt_secret_key,
            algorithm=app_config.jwt_algorithm,
        )

    def _get_token_expiration_time(self, token_lifetime: int) -> str:
        result = (
            datetime.datetime.now() + datetime.timedelta(minutes=token_lifetime)
        ).strftime(app_config.jwt_datetime_pattern)
        return result

    def store_refresh_token(self, token: RefreshToken) -> None:
        """Сохранить данные refresh токена.

        В момент перевыпуска понадобится, чтобы избежать мошенничества с
        перевыпуском новой пары по одному и тому же токену несколько
        раз.
        """

        self.jwt_storage.store_refresh_token(
            jti=token.jti,
            user_id=token.user_id,
            expire_time=token.expired,
        )

        return None

    def is_refresh_token(self, decoded_token: Union[RefreshToken, AccessToken]):
        """Проверка является ли токен refresh-токеном."""
        if decoded_token.type != app_config.refresh_token_type:
            raise exc.ApiTokenWrongTypeException

    def decode(self, encoded_token: str) -> Union[RefreshToken, AccessToken]:
        """Вернуть декодированные данные jwt-токена."""
        try:
            token_data = jwt.decode(
                encoded_token,
                app_config.jwt_secret_key,
                algorithms=[
                    app_config.jwt_algorithm,
                ],
            )
        except jwt.ExpiredSignatureError:
            raise exc.ApiTokenValidationException(
                detail="Не удалось декодировать токен"
            )
        except jwt.InvalidSignatureError:
            raise exc.ApiTokenValidationException

        if "type" not in token_data:
            raise exc.ApiTokenValidationException(
                detail="Отсутствует обязательное поле 'type'"
            )

        if token_data["type"] == app_config.refresh_token_type:
            token = RefreshToken.parse_obj(token_data)
        elif token_data["type"] == app_config.access_token_type:
            token = AccessToken.parse_obj(token_data)
        else:
            raise exc.ApiTokenValidationException(detail="Тип токена не валиден")

        token._encoded_token = encoded_token

        return token

    def is_expired(self, token: Union[RefreshToken, AccessToken]) -> None:
        """Проверка, истекло ли время жизни токена Если истекло выбрасывается
        исключение ApiTokenValidationException."""
        if datetime.datetime.now() >= token.expired:
            raise exc.ApiTokenValidationException(detail="Время жизни истекло")

        return None

    def is_in_blacklist(self, token: AccessToken) -> None:
        """Проверка access токена на нахождение в чёрном списке. Чёрный список
        access токенов формируется в момент:

        - разлогина (/logout)
        - обновления пары токенов по refresh токену (/refresh_token)
        """
        bl_data = self._black_list_storage.get_data(jti=str(token.jti))

        if bl_data:
            raise exc.ApiTokenValidationException(detail="Токен был отозван ранее")

        return None

    def get_refresh_tokens_jti(self, user_id):
        """Получить все jti refresh-токенов по id пользователя."""
        all_user_refresh_jti = self.jwt_storage.get_refresh_tokens_jti(user_id)

        return all_user_refresh_jti

    def remove_refresh_tokens(self, all_user_refresh_jti: List[str]) -> None:
        """Удалить все записи о refresh-токенах."""
        self.jwt_storage.remove_refresh_tokens(all_user_refresh_jti)

    def put_tokens_to_black_list(self, jti: str) -> None:
        """Положить jti токенa в черный список.

        В дальнейшем при попытке доступа с access-токено имеющим jti,
        который находится в черном списке, пользователь получит отказ в
        доступе.
        """

        self._black_list_storage.set_data(jti=jti)
