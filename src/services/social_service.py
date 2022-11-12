from models.api.social_account import InputSocialAccount
from storage.social_storage import ISocialAccountStorage


class SocialAccountService:
    """Класс сервиса Социальный аккаунт.

    Содержит общий код, для работы с сущностью Социальный аккаунт.
    """

    def __init__(
            self,
            social_storage: ISocialAccountStorage
    ):
        self.social_storage = social_storage

    def get_soc_account(self, id):
        return self.social_storage.get_soc_account(id)

    def filter_soc_account(self, **kwargs):
        return self.social_storage.filter_soc_account(**kwargs)

    def create_soc_account(self, social_input: InputSocialAccount):
        return self.social_storage.create_soc_account(**social_input.dict())
