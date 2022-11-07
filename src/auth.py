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

    oauth.register(
        name='facebook',
        client_id=app.config.get('FACEBOOK_CLIENT_ID'),
        client_secret=app.config.get('FACEBOOK_CLIENT_SECRET'),
        access_token_url=app.config.get('FACEBOOK_ACCESS_TOKEN_URL'),
        access_token_params=app.config.get('FACEBOOK_ACCESS_TOKEN_PARaMS'),
        authorize_url=app.config.get('FACEBOOK_AUTHORIZE_URL'),
        authorize_params=app.config.get('FACEBOOK_AUTHORIZE_URL'),
        api_base_url=app.config.get('FACEBOOK_API_BASE_URL'),
        client_kwargs=app.config.get('FACEBOOK_CLIENT_KWARGS'),
    )
