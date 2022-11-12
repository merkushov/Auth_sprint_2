import abc

from db import db
from models.db.auth_model import SocialAccount


class ISocialAccountStorage(abc.ABC):
    @abc.abstractmethod
    def get_soc_account(self, id):
        """Получение социального аккаунта."""

    @abc.abstractmethod
    def filter_soc_account(self, **sa_kwargs):
        """Фильтрация социальных аккаунтов."""

    @abc.abstractmethod
    def create_soc_account(self, **sa_kwargs):
        """Создание записи о входе через социальный аккаунт."""


class PostgresSocialAccountStorage(ISocialAccountStorage):
    def get_soc_account(self, id):
        return SocialAccount.query.get(id)

    def filter_soc_account(self, **sa_kwargs):
        return SocialAccount.query.filter_by(**sa_kwargs)

    def create_soc_account(self, user_id, social_id, social_name):
        soc_acc = SocialAccount(user_id=user_id, social_id=social_id, social_name=social_name)
        db.session.add(soc_acc)

        db.session.commit()

        return soc_acc
