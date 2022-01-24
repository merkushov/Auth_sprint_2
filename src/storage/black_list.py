import abc
from typing import Optional

from config import Config
from redis_client import redis_client


class IBlackListStorage:
    """Базовый абстрактный класс хранилища данных для невалдных токенов."""

    @abc.abstractmethod
    def _key(self, jti: str) -> str:
        pass

    @abc.abstractmethod
    def set_data(self, jti: str) -> Optional[bool]:
        pass

    @abc.abstractmethod
    def get_data(self, jti: str) -> None:
        pass


class RedisBlackListStorage(IBlackListStorage):
    def _key(self, jti: str) -> str:
        return f"black_list.access_token.{jti}"

    def get_data(self, jti: str) -> Optional[str]:
        data = redis_client.get(self._key(jti))

        if data:
            return str(data)

        return None

    def set_data(self, jti: str) -> None:
        redis_client.set(self._key(jti), jti, ex=Config.ACCESS_TOKEN_LIFETIME * 60)
        return None
