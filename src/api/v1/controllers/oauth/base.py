from abc import ABC, abstractmethod

from flask import request

from services import UserService, get_user_service
from services import AuthService, get_auth_service
from models.api.user import InputCreateUser
from utils.password import random_password


from exceptions import (
    ApiUserNotFoundException,
)


class OAuthController(ABC):
    def __init__(
            self,
            user_service: UserService = get_user_service(),
            auth_service: AuthService = get_auth_service()
    ):
        self.user_service: UserService = user_service
        self.auth_service: AuthService = auth_service

    @property
    @abstractmethod
    def oauth_provider_stamp(self):
        pass

    @property
    @abstractmethod
    def oauth_provider(self):
        """Провайдер данных для аутентификации"""
        pass

    @property
    @abstractmethod
    def redirect_url(self):
        """URL для редиректа после аутентификации"""
        pass

    def login(self):
        """Логин пользователя через Яндекс Oauth2."""
        return self.oauth_provider.authorize_redirect(request, self.redirect_url)

    def callback(self):
        """Получение подтверждения от провайдера и выдача токенов"""

        token = self.oauth_provider.authorize_access_token(request)
        resp = self.oauth_provider.get('email', token=token)

        resp.raise_for_status()
        email = resp.json()

        status_code = 200
        # если юзера нет в бд, то сгенерим для него пароль
        try:
            usr = self.user_service.get_user(email=email.get(email))
        except ApiUserNotFoundException:
            usr_input = InputCreateUser(
                email=email.get('email'),
                password=random_password(),
            )
            usr = self.user_service.create_user(usr_input)
            # при интеграции с фронтом, он будет отправлять пользователя на форму для обновления пароля при этом коде
            status_code = 201

        return self.authorize(user=usr), status_code

    def authorize(self, user):
        """Авторизация и выдача токенов доступа после универсального логина"""

        auth_method_stamp = f" : {user.email} {self.oauth_provider_stamp} OAuth2"
        self.user_service.create_access_history(user,
                                                request.headers["User-Agent"] + auth_method_stamp
                                                )
        return self.auth_service.issue_tokens(user)
