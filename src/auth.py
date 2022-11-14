from authlib.integrations.flask_client import OAuth
from config import app_config

oauth = OAuth()


def init_oauth(app):
    # Инициализация фласк-клиента после запроса службы
    oauth.init_app(app)

    # Регистрация провайдеров
    oauth.register(
        name='yandex',
        access_token_url='https://oauth.yandex.ru/token',
        access_token_params=None,
        authorize_url='https://oauth.yandex.ru/authorize',
        authorize_params=None,
        client_kwargs={'scope': 'login:email login:info'},
        client_id=app_config.oauth2.yandex_client_id,
        client_secret=app_config.oauth2.yandex_client_secret,
    )

    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        },
        client_id=app_config.oauth2.google_client_id,
        client_secret=app_config.oauth2.google_client_secret,
    )

    oauth.register(
        name='facebook',
        client_id=app_config.oauth2.facebook_client_id,
        client_secret=app_config.oauth2.facebook_client_secret,
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'openid email'},
        server_metadata_url='https://www.facebook.com/.well-known/openid-configuration'
    )
