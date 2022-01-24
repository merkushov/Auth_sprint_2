import abc
import datetime
import logging
from typing import List
from uuid import UUID

from db import db
from exceptions import ApiTokenNotFoundException
from models.db.auth_model import RefreshJwt


class IJwtStorage:
    """Базовый абстрактный класс хранилища jwt-токенов."""

    @abc.abstractmethod
    def store_refresh_token(
        self, jti: UUID, user_id: UUID, expire_time: datetime.datetime
    ) -> None:
        """Сохранить refresh-токен в БД."""

    @abc.abstractmethod
    def remove_refresh_token(self, jti: UUID) -> None:
        """Сохранить refresh-токен в БД."""

    @abc.abstractmethod
    def get_refresh_token(self, jti: str) -> str:
        """Вернуть refresh токен по jti."""

    @abc.abstractmethod
    def get_refresh_tokens_jti(self, user_id: str) -> List[str]:
        """Вернуть список jti-идентификаторов всех refresh-токен по id
        пользователя."""

    @abc.abstractmethod
    def remove_refresh_tokens(self, tokens_jti: List[str]):
        """Удалить все записи refresh-токенов."""


class PostgresJwtStorage(IJwtStorage):
    def remove_refresh_tokens(self, tokens_jti: List[str]):
        for jti in tokens_jti:
            db.session.query(RefreshJwt).filter(RefreshJwt.id == jti).delete()

        db.session.commit()

    def get_refresh_tokens_jti(self, user_id: str) -> List[str]:
        tokens: List[RefreshJwt] = RefreshJwt.query.filter(
            RefreshJwt.user_id == user_id
        ).all()

        all_jti = [str(token.id) for token in tokens]

        return all_jti

    def remove_refresh_token(self, jti: UUID) -> None:
        deleted_rows = (
            db.session.query(RefreshJwt).filter(RefreshJwt.id == jti).delete()
        )
        db.session.commit()

        if deleted_rows == 0:
            logging.warning(f"Попытка удалить несуществующий refresh токен. jti: {jti}")

        return None

    def get_refresh_token(self, jti: str) -> RefreshJwt:
        token = RefreshJwt.query.filter(RefreshJwt.id == jti).first()
        if not token:
            raise ApiTokenNotFoundException

        return token

    def store_refresh_token(
        self, jti: UUID, user_id: UUID, expire_time: datetime.datetime
    ) -> None:
        token = RefreshJwt(
            id=jti,
            user_id=user_id,
            expire=expire_time,
        )
        db.session.add(token)
        db.session.commit()

        return None
