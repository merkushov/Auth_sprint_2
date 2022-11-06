from flask import request, url_for

from auth import oauth
from services import UserService, get_user_service
from services import AuthService, get_auth_service
from api.v1.controllers.oauth.base import OAuthController


class YandexOAuthController(OAuthController):

    def __init__(
            self,
            user_service: UserService = get_user_service(),
            auth_service: AuthService = get_auth_service()
    ):
        super(YandexOAuthController, self).__init__(user_service=user_service, auth_service=auth_service)

    @property
    def redirect_url(self):
        return "api/v1/login/yandex/authorize" # TODO: взять урл из роутинга

    @property
    def oauth_provider(self):
        return oauth.yandex

    @property
    def oauth_provider_stamp(self):
        return "Yandex"
