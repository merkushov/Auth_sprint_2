from abc import ABC, abstractmethod
from http import HTTPStatus
from logging import getLogger

from flask import request

from exceptions import ApiUserNotFoundException
from models.api.social_account import (
    InputSocialAccount,
    OAuthProvider,
    ParsedToken,
    UserInfo,
)
from models.api.user import InputCreateProviderUser, User
from services import (
    AuthService,
    SocialAccountService,
    UserService,
    get_auth_service,
    get_social_account_service,
    get_user_service,
)

logger = getLogger(__name__)


class OAuthController(ABC):
    oauth_provider_stamp: str = None

    def __init__(
            self,
            user_service: UserService = get_user_service(),
            auth_service: AuthService = get_auth_service(),
            social_acc_service: SocialAccountService = get_social_account_service(),
    ):
        self.user_service: UserService = user_service
        self.auth_service: AuthService = auth_service
        self.social_acc_service: SocialAccountService = social_acc_service

    @property
    @abstractmethod
    def oauth_provider(self):
        """Провайдер данных для аутентификации."""
        pass

    @property
    @abstractmethod
    def redirect_url(self) -> str:
        """URL для редиректа после аутентификации."""
        pass

    @abstractmethod
    def _get_social_data(self, *args, **kwargs) -> ParsedToken:
        """Получение идентификатора пользователя и провайдера."""

    def login(self):
        """Логин пользователя через Oauth2."""
        return self.oauth_provider.authorize_redirect(redirect_uri=self.redirect_url)

    def callback(self):
        """Получение подтверждения от провайдера и выдача токенов."""

        token = self.oauth_provider.authorize_access_token()
        logger.debug(token)

        parsed_token = self._get_social_data(token)

        logger.debug(parsed_token)
        new_provider_user = InputCreateProviderUser(
            email=parsed_token.user_info.email,
        )

        response, status_code = self.insert(new_provider_user=new_provider_user, parsed_token=parsed_token)

        return response, status_code

    def authorize(self, user: User):
        """Авторизация и выдача токенов доступа после универсального логина."""

        auth_method_stamp = f" : {user.email} {self.oauth_provider_stamp} OAuth2"
        self.user_service.create_access_history(user,
                                                request.headers["User-Agent"] + auth_method_stamp
                                                )
        token_pair = self.auth_service.issue_tokens(user)
        logger.debug("OAuth issued tokens: " + repr(token_pair))

        return {
            "access": token_pair.access.encoded_token,
            "refresh": token_pair.refresh.encoded_token
        }

    def insert(self, parsed_token: ParsedToken, new_provider_user: InputCreateProviderUser):
        try:
            # проверим есть ли пользователь по идентификатору во внешнем сервисе
            usr = self.user_service.get_user_by_social_id(
                social_id=parsed_token.social_id, social_name=parsed_token.social_name
            )
            status_code = HTTPStatus.OK
            response = self.authorize(user=usr)
        except ApiUserNotFoundException:
            try:
                usr = self.user_service.get_user(email=new_provider_user.email)
            except ApiUserNotFoundException:
                # если такого пользователя нет, то создадим юзера и запись о входе через внешний сервис
                response, status_code = self._create_user_with_social(
                    new_provider_user=new_provider_user, parsed_token=parsed_token
                )
            else:
                response, status_code = self._create_social(user=usr, parsed_token=parsed_token)

        return response, status_code

    def _create_user_with_social(self, new_provider_user: InputCreateProviderUser, parsed_token: ParsedToken):
        """Создание пользователя и социального аккаунта"""
        # если такого пользователя нет, то создадим юзера
        user = self.user_service.create_user(user=new_provider_user)
        return self._create_social(user=user, parsed_token=parsed_token)

    def _create_social(self, user: User, parsed_token: ParsedToken):
        """Проверка наличия наличия социального аккаунта, уже имеющегося email и username"""
        # создадим запись о входе через внешний сервис
        new_sa = InputSocialAccount(
            user_id=user.id,
            social_id=parsed_token.social_id,
            social_name=parsed_token.social_name,
        )
        self.social_acc_service.create_soc_account(social_input=new_sa)
        return self.authorize(user=user), HTTPStatus.CREATED


class OpenIDOAuthController(OAuthController, ABC):
    def _get_social_data(self, token, *args, **kwargs) -> ParsedToken:
        user_info = token['userinfo']
        return ParsedToken(
            social_id=user_info['sub'],
            social_name=self.oauth_provider_stamp,
            user_info=UserInfo(
                email=user_info['email'],
            )
        )