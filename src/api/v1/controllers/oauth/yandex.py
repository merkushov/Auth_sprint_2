from flask import url_for

from api.v1.controllers.oauth.base import OAuthController
from auth import oauth
from services import AuthService, UserService, get_auth_service, get_user_service


class YandexOAuthController(OAuthController):
    oauth_provider_stamp = "Yandex"
    email_field = 'login:email'

    def __init__(
            self,
            user_service: UserService = get_user_service(),
            auth_service: AuthService = get_auth_service()
    ):
        super(YandexOAuthController, self).__init__(user_service=user_service, auth_service=auth_service)

    @property
    def redirect_url(self):
        return url_for('api.v1.yandex_authorize', _external=True)

    @property
    def oauth_provider(self):
        return oauth.yandex

