from flask import url_for

from api.v1.controllers.oauth.base import OAuthController
from auth import oauth


class GoogleOAuthController(OAuthController):
    @property
    def oauth_provider(self):
        return oauth.google

    @property
    def redirect_url(self):
        return url_for('google_authorize')

    @property
    def oauth_provider_stamp(self):
        return "Google"

    @property
    def email_field(self) -> str:
        return 'email'
