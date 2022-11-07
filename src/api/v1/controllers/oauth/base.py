from abc import ABC, abstractmethod
from http import HTTPStatus

from flask import request

from exceptions import ApiUserNotFoundException
from models.api.social_account import InputSocialAccount
from models.api.user import InputCreateProviderUser
from services import (
    AuthService,
    SocialAccountService,
    UserService,
    get_auth_service,
    get_social_account_service,
    get_user_service,
)


class OAuthController(ABC):
    def __init__(
            self,
            user_service: UserService = get_user_service(),
            auth_service: AuthService = get_auth_service(),
            social_acc_service: SocialAccountService = get_social_account_service(),
    ):
        self.user_service: UserService = user_service
        self.auth_service: AuthService = auth_service
        self.social_acc_service: SocialAccountService = social_acc_service

    @property
    @abstractmethod
    def oauth_provider_stamp(self):
        pass

    @property
    @abstractmethod
    def oauth_provider(self):
        """Провайдер данных для аутентификации."""
        pass

    @property
    @abstractmethod
    def redirect_url(self) -> str:
        """URL для редиректа после аутентификации."""
        pass

    @property
    @abstractmethod
    def email_field(self) -> str:
        """Название поля, по которому можно получить email."""

    def login(self):
        """Логин пользователя через Яндекс Oauth2."""
        return self.oauth_provider.authorize_redirect(self.redirect_url)

    def callback(self):
        """Получение подтверждения от провайдера и выдача токенов."""

        token = self.oauth_provider.authorize_access_token()
        user_info = token['userinfo']

        new_provider_user = InputCreateProviderUser(
            email=user_info.get(self.email_field),
        )
        status_code = HTTPStatus.OK

        # если юзера нет в бд, то сгенерим для него пароль
        try:
            usr = self.user_service.get_user_by_social_id(social_id=..., social_name=...)
        except ApiUserNotFoundException:
            usr = self.user_service.create_user(new_provider_user)

            new_sa = InputSocialAccount(
                user_id=usr.id,
                social_id=self.oauth_provider.get('id_token'),
                social_name=self.oauth_provider_stamp,
            )
            self.social_acc_service.create_soc_account(social_input=new_sa)
            # при интеграции с фронтом, он будет отправлять пользователя на форму для обновления пароля при этом коде
            status_code = HTTPStatus.CREATED

        return self.authorize(user=usr), status_code

    def authorize(self, user):
        """Авторизация и выдача токенов доступа после универсального логина."""

        auth_method_stamp = f" : {user.email} {self.oauth_provider_stamp} OAuth2"
        self.user_service.create_access_history(user,
                                                request.headers["User-Agent"] + auth_method_stamp
                                                )
        return self.auth_service.issue_tokens(user)
