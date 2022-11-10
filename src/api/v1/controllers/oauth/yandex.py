from flask import url_for

from api.v1.controllers.oauth.base import OAuthController
from auth import oauth
from models.api.social_account import OAuthProvider, ParsedToken, UserInfo
from services import AuthService, UserService, get_auth_service, get_user_service



class YandexOAuthController(OAuthController):
    oauth_provider_stamp = OAuthProvider.yandex.name

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

    def _get_social_data(self, token, *args, **kwargs) -> ParsedToken:
        resp = self.oauth_provider.get(
            'https://login.yandex.ru/info',
            token=token,
            params={"format": 'json', "with_openid_identity": 'yes'}
        )
        resp.raise_for_status()
        profile = resp.json()

        return ParsedToken(
            social_id=profile['client_id'],
            social_name=self.oauth_provider_stamp,
            user_info=UserInfo(
                email=profile['default_email'],
            )
        )


