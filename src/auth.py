from authlib.integrations.flask_client import OAuth


oauth = OAuth()

def init_oauth(app):
    # Инициализация фласк-клиента после запроса службы
    oauth.init_app(app)

    # Регистрация провайдеров
    oauth.register(
        name='yandex',
        client_id='96c8e29b9b294b8f9e94484086c998b7',
        client_secret='5579f23df4854f7e9376de50cd4a4766',
        access_token_url='https://oauth.yandex.ru/authorize',
        access_token_params=None,
        authorize_url='https://oauth.yandex.ru/token',
        authorize_params=None,
        api_base_url='https://api.yandex.ru/',
        client_kwargs={'scope': 'openid login email'},
    )