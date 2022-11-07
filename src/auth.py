from authlib.integrations.flask_client import OAuth


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
        client_id=app.config.get("OAUTH2_YANDEX_CLIENT_ID"),
        client_secret=app.config.get("OAUTH2_YANDEX_CLIENT_SECRET"),
    )

    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        },
        client_id=app.config.get("OAUTH2_GOOGLE_CLIENT_ID"),
        client_secret=app.config.get("OAUTH2_GOOGLE_CLIENT_SECRET"),
    )