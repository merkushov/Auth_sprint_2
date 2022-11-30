from flask import Blueprint, Flask

import api.v1.controllers as api_v1_c
from models.api.social_account import OAuthProvider

def init_routes(app: Flask):
    api = Blueprint("api", __name__, url_prefix="/api")
    api_v1 = Blueprint("v1", __name__, url_prefix="/v1")

    setup_v1_routes(api_v1)

    api.register_blueprint(api_v1)
    app.register_blueprint(api)


def setup_v1_routes(api_v1: Blueprint):

    # Добавить OAuth эндпоинты в целевое АПИ
    api_v1.add_url_rule(
        f"/login/{OAuthProvider.yandex.name}",
        f"{OAuthProvider.yandex.name}",
        view_func=api_v1_c.get_yandex_oauth_controller().login,
        methods=[
            "GET",
        ],
    )
    api_v1.add_url_rule(
        f"/login/{OAuthProvider.yandex.name}/authorize",
        f"{OAuthProvider.yandex.name}_authorize",
        view_func=api_v1_c.get_yandex_oauth_controller().callback,
        methods=[
            "GET",
        ],
    )
    api_v1.add_url_rule(
        f"/login/{OAuthProvider.facebook.name}",
        f"{OAuthProvider.facebook.name}",
        view_func=api_v1_c.get_fb_oauth_controller().login,
        methods=[
            "GET",
        ],
    )
    api_v1.add_url_rule(
        f"/login/{OAuthProvider.facebook.name}/authorize",
        f"{OAuthProvider.facebook.name}_authorize",
        view_func=api_v1_c.get_fb_oauth_controller().callback,
        methods=[
            "GET",
        ],
    )
    api_v1.add_url_rule(
        f"/login/{OAuthProvider.google.name}",
        f"{OAuthProvider.google.name}",
        view_func=api_v1_c.get_google_oauth_controller().login,
        methods=[
            "GET",
        ],
    )
    api_v1.add_url_rule(
        f"/login/{OAuthProvider.google.name}/authorize",
        f"{OAuthProvider.google.name}_authorize",
        view_func=api_v1_c.get_google_oauth_controller().callback,
        methods=[
            "GET",
        ],
    )

    api_v1.add_url_rule(
        "/ping",
        "ping",
        view_func=api_v1_c.get_health_check_controller().ping,
        methods=[
            "GET"
        ],
    )

    api_v1.add_url_rule(
        "/login",
        "login",
        view_func=api_v1_c.get_auth_controller().login,
        methods=[
            "POST",
        ],
    )

    api_v1.add_url_rule(
        "/user",
        "register_user",
        view_func=api_v1_c.get_auth_controller().register_user,
        methods=[
            "POST",
        ],
    )

    api_v1.add_url_rule(
        "/me/refresh_token",
        "refresh_token",
        view_func=api_v1_c.get_auth_controller().refresh_token,
        methods=[
            "PUT",
        ],
    )

    api_v1.add_url_rule(
        "/me",
        "update_current_user",
        view_func=api_v1_c.get_user_controller().update_current_user,
        methods=[
            "PUT",
        ],
    )

    api_v1.add_url_rule(
        "/me",
        "get_current_user_info",
        view_func=api_v1_c.get_user_controller().get_current_user_info,
        methods=[
            "GET",
        ],
    )

    api_v1.add_url_rule(
        "/me/roles",
        "get_my_roles",
        view_func=api_v1_c.get_user_controller().get_my_roles,
        methods=[
            "GET",
        ],
    )

    api_v1.add_url_rule(
        "/me/access_history",
        "get_access_history",
        view_func=api_v1_c.get_access_history_controller().get_access_history,
        methods=["GET"],
    )

    api_v1.add_url_rule(
        "/me/logout",
        "logout",
        view_func=api_v1_c.get_auth_controller().logout,
        methods=[
            "GET",
        ],
    )

    api_v1.add_url_rule(
        "/me/logout_other_devices",
        "logout_other_devices",
        view_func=api_v1_c.get_auth_controller().logout_other_devices,
        methods=[
            "GET",
        ],
    )

    api_v1.add_url_rule(
        "/role",
        "get_roles",
        view_func=api_v1_c.get_role_controller().get_roles,
        methods=[
            "GET",
        ],
    )

    api_v1.add_url_rule(
        "/role/<role_id>",
        "get_role",
        view_func=api_v1_c.get_role_controller().get_role,
        methods=[
            "GET",
        ],
    )

    api_v1.add_url_rule(
        "/role",
        "create_role",
        view_func=api_v1_c.get_role_controller().create_role,
        methods=[
            "POST",
        ],
    )

    api_v1.add_url_rule(
        "/role/<role_id>",
        "update_role",
        view_func=api_v1_c.get_role_controller().update_role,
        methods=[
            "PUT",
        ],
    )

    api_v1.add_url_rule(
        "/role/<role_id>",
        "delete_role",
        view_func=api_v1_c.get_role_controller().delete_role,
        methods=[
            "DELETE",
        ],
    )

    api_v1.add_url_rule(
        "/user/<user_id>/role/<role_id>",
        "check_user_role",
        view_func=api_v1_c.get_user_controller().check_user_role,
        methods=[
            "GET",
        ],
    )

    api_v1.add_url_rule(
        "/user/<user_id>/role/<role_id>",
        "set_role_to_user",
        view_func=api_v1_c.get_user_controller().set_role_to_user,
        methods=[
            "POST",
        ],
    )

    api_v1.add_url_rule(
        "/user/<user_id>/role/<role_id>",
        "delete_user_role",
        view_func=api_v1_c.get_user_controller().delete_user_role,
        methods=[
            "DELETE",
        ],
    )
