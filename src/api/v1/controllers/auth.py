from http import HTTPStatus as status

from flask import jsonify, request

from api.helpers import auth_required
from models.api.tokens import AccessToken, InputRefreshToken, TokenPair
from models.api.user import InputCreateUser, InputLoginUser, User
from services import (
    AuthService,
    JWTService,
    UserService,
    get_auth_service,
    get_jwt_service,
    get_user_service,
)


class AuthController:
    def __init__(
        self,
        auth_service: AuthService = get_auth_service(),
        user_service: UserService = get_user_service(),
        jwt_service: JWTService = get_jwt_service(),
    ):
        self.auth_service = auth_service
        self.user_service = user_service
        self.jwt_service = jwt_service

    def login(self):
        """Логин пользователя."""

        user_input_data = InputLoginUser.parse_obj(request.json)

        user = self.user_service.get_user(username=user_input_data.username)
        self.user_service.validate_password(user, user_input_data.password)

        auth_method_stamp = " : Password validated"
        self.user_service.create_access_history(user, 
            request.headers["User-Agent"] + auth_method_stamp
        )

        token_pair = self.auth_service.issue_tokens(user)

        return {
            "access": token_pair.access.encoded_token,
            "refresh": token_pair.refresh.encoded_token,
        }, status.OK

    def register_user(self):
        """Зарегистрировать нового пользователя."""

        user_input_data = InputCreateUser.parse_obj(request.json)
        user_data: User = self.user_service.create_user(user_input_data)

        return jsonify(user_data.dict()), status.CREATED

    def refresh_token(self):
        """Обновить пару токенов access и refresh токены.

        Для этого нужно передать сюда refresh токен.
        """
        input_refresh_token = InputRefreshToken.parse_obj(request.json)

        token_pair: TokenPair = self.auth_service.refresh_token(
            input_refresh_token.refresh_token
        )

        return {
            "access": token_pair.access.encoded_token,
            "refresh": token_pair.refresh.encoded_token,
        }, status.OK

    @auth_required
    def logout(self, access_token: AccessToken):
        """Логаут пользователя."""
        self.jwt_service.put_tokens_to_black_list(access_token.jti)

        return {}, status.OK

    @auth_required
    def logout_other_devices(self, access_token: AccessToken):
        """Логаут пользователя из всех устройств, кроме текущего."""
        jti, user_id = access_token.jti, access_token.user_id

        all_user_refresh_jti = self.jwt_service.get_refresh_tokens_jti(user_id)

        if jti in all_user_refresh_jti:
            all_user_refresh_jti.remove(jti)

        if not all_user_refresh_jti:
            return {}, status.OK

        self.jwt_service.remove_refresh_tokens(all_user_refresh_jti)

        for jti in all_user_refresh_jti:
            self.jwt_service.put_tokens_to_black_list(jti)

        return {}, status.OK
