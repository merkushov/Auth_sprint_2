from flask import url_for

from api.v1.controllers.oauth.base import OAuthController
from auth import oauth


class FBOAuthController(OAuthController):
    @property
    def redirect_url(self):
        return url_for('facebook_authorize')

    @property
    def oauth_provider(self):
        return oauth.facebook

    @property
    def oauth_provider_stamp(self):
        return "Facebook"

    @property
    def email_field(self) -> str:
        return ...
