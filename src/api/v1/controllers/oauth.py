
from flask import request, url_for, redirect

from auth import oauth
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
        return self.auth_service.issue_tokens(user)

    def yandex(self):
        """Логин пользователя через Яндекс Oauth2."""

        redirect_uri = url_for('api/v1/login/authorize/yandex')
        return self.oauth.yandex.authorize_redirect(request, redirect_uri)
    
    def yandex_authorize(self):
        """Получение подтверждения от провайдера и выдача токенов"""

        token = self.oauth.yandex.authorize_access_token(request)
        resp = self.oauth.yandex.get('email', token=token)
        resp.raise_for_status()
        email = resp.json()
        return email

        # return self.authorize(
        #     user={{
        #     'email': email,
        #           }}, method='Yandex')

    def google(self):
        """Логин пользователя через Google Oauth2."""
        
        """Данные универсального логина после привязки аккаунта к базе"""
        user_input_data = InputLoginUser.parse_obj({
            'username': 'ilya3',
            'email': 'from@gmail.com',
        })

        user = self.user_service.get_user(username=user_input_data.username)
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