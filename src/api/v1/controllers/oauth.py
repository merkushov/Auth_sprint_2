from flask import request, url_for
from http import HTTPStatus as status

from auth import oauth
from models.api.user import InputCreateProviderUser, User
from services import UserService, get_user_service
from services import AuthService, get_auth_service

from models.api.user import InputLoginUser


class OAuthController:
    def __init__(
        self,
        user_service: UserService = get_user_service(),
        auth_service: AuthService = get_auth_service()
    ):
        self.user_service: UserService = user_service
        self.auth_service: AuthService = auth_service
        self.oauth = oauth

    def authorize(self, user, method):
        """Авторизация и выдача токенов доступа после универсального логина"""

        auth_method_stamp = f" : {user.email} {method} OAuth2"
        self.user_service.create_access_history(user,
            request.headers["User-Agent"] + auth_method_stamp
        )
        token_pair = self.auth_service.issue_tokens(user)

        return {
            "access": token_pair.access.encoded_token,
            "refresh": token_pair.refresh.encoded_token,
        }, status.OK

    def yandex(self):
        """Логин пользователя через Яндекс Oauth2."""

        redirect_uri = url_for('api.v1.yandex_authorize', _external=True)
        return self.oauth.yandex.authorize_redirect(redirect_uri)

    def yandex_authorize(self):
        """Получение подтверждения от провайдера и выдача токенов"""

        token = self.oauth.yandex.authorize_access_token()
        resp = self.oauth.yandex.get('login:email', token=token)
        resp.raise_for_status()

        new_provider_user = InputCreateProviderUser(
            email=resp.json(),
        )

        user: User = self.user_service.get_user(username=new_provider_user.username)
        if not user:
            self.user_service.create_user(new_provider_user)

        return self.authorize(user, "Yandex")

    def google(self):
        """
        Логин пользователя через Google Oauth2.
        Эндпоинт редиректит пользователя на форму авторизации Google.
        """

        redirect_uri = url_for('google_authorize', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    def universal(self, provider_authorize):
        redirect_uri = url_for(provider_authorize, _external=True)


    def google_authorize(self):
        """Получение подтверждения от провайдера и выдача токенов"""

        token = oauth.google.authorize_access_token()
        user_info = token['userinfo']

        new_provider_user = InputCreateProviderUser(
            email=user_info.get("email"),
        )

        user: User = self.user_service.get_user(username=new_provider_user.username)
        if not user:
            self.user_service.create_user(new_provider_user)

        return self.authorize(user, "Google")

    def facebook(self):
        """Логин пользователя через Facebook Oauth2."""

        """Данные универсального логина после привязки аккаунта к базе"""
        user_input_data = InputLoginUser.parse_obj({
            'username': 'ilya3',
            'email': 'from@gmail.com',
        })

        user = self.user_service.get_user(username=user_input_data.username)
        return self.authorize(user, "Facebook")

