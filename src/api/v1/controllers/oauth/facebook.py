from api.v1.controllers.oauth.base import OAuthController
from auth import oauth


class FBOAuthController(OAuthController):
    @property
    def redirect_url(self):
        return "api/v1/login/authorize/facebook"

    @property
    def oauth_provider(self):
        return oauth.facebook

    @property
    def oauth_provider_stamp(self):
        return "Facebook"
