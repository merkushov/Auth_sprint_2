from api.v1.controllers.oauth.base import OAuthController
from auth import oauth


class GoogleOAuthController(OAuthController):
    @property
    def oauth_provider(self):
        return oauth.google

    @property
    def redirect_url(self):
        return

    @property
    def oauth_provider_stamp(self):
        return "Google"
