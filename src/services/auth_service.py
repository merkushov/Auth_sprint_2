from models.api.tokens import RefreshToken, TokenPair
from services.jwt_service import JWTService
from storage import IBlackListStorage
from storage.jwt_storage import IJwtStorage
from storage.user_storage import IUserStorage


class AuthService:
    """Класс сервиса авторизации.

    Содержит методы эндпоинтов сервиса.
    """

    def __init__(
        self,
        user_storage: IUserStorage,
        jwt_storage: IJwtStorage,
        jwt_service: JWTService,
        black_list_storage: IBlackListStorage,
    ):

        self.user_storage = user_storage
        self.jwt_storage = jwt_storage
        self.jwt_service = jwt_service
        self.black_list_storage = black_list_storage

    def issue_tokens(self, user):
        """Выдать пару токенов access и refresh токены после логина."""

        token_pair = self.jwt_service.create_token_pair(user=user)
        self.jwt_service.store_refresh_token(token_pair.refresh)

        return token_pair

    def refresh_token(self, encoded_refresh_token: str) -> TokenPair:
        """Обновить пару токенов access и refresh токены по refresh токену.

        Сценарий обновления:
         - раскодировать refresh токен
         - проверить время жизни
         - убедиться, что это валидный токен
            и им ещё не пользовались для перевыпуска пары (запрос в БД по jti)
         - сгенерировать новую пару токенов (access + refresh)
         - сохранить jti новой пары токенов в БД
         - удалить запись о старом refresh токене (по jti)
         - помечаем текущий access токен как не валидный (в Redis по jti)

        В случае любой ошибки генерируется местное исключение, которое
        будет обработано на уровне фреймворка. Клиент получит ожидаемый ответ.

        На выходе, метод возвращает пару токенов access+refresh
        """

        # раскодировать токен
        refresh_token: RefreshToken = self.jwt_service.decode(
            encoded_token=encoded_refresh_token
        )

        # проверка, что передан именно refresh-токен
        self.jwt_service.is_refresh_token(refresh_token)

        # истекло ли времени жизни токена
        self.jwt_service.is_expired(token=refresh_token)

        # валидация данных по БД:
        #   получение записи из БД позволяет предположить, что этот токен
        #   ещё не был использоват для обновления пары
        self.jwt_storage.get_refresh_token(jti=refresh_token.jti)

        user = self.user_storage.get_user(refresh_token.user_id)

        # формируем новую пару токенов (access+refresh)
        token_pair: TokenPair = self.jwt_service.create_token_pair(user=user)

        # сохраняем информацию о том что создали новую пару
        # Храним данные по уникальному ключу пары - jti

        self.jwt_storage.store_refresh_token(
            jti=token_pair.jti, user_id=user.id, expire_time=token_pair.refresh.expired
        )

        # удаляем старый refresh-токен из базы
        self.jwt_storage.remove_refresh_token(jti=refresh_token.jti)

        # добавляем jti (идентификатор пары) старого токена в черный список
        # нужно, чтобы сразу же никто не мог войти по старому access-токену
        self.black_list_storage.set_data(jti=str(refresh_token.jti))

        return token_pair
