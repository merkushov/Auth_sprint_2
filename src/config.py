import os
from pathlib import Path
from pydantic import BaseSettings, Field, root_validator

from dotenv import load_dotenv

load_dotenv()


class DBSettings(BaseSettings):
    host: str
    db: str
    user: str
    password: str

    class Config:
        env_prefix = 'postgres_'
        env_nested_delimiter = '_'

    def uri(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}/{self.db}"


class DBSettingsTest(DBSettings):
    db: str = Field(default="POSTGRES_DB_TEST")


class RedisSettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=6379)
    db: int = Field(default=0)

    class Config:
        env_prefix = 'redis_'
        env_nested_delimiter = '_'

    def url(self):
        return f"redis://{self.host}:{self.port}/{self.db}"


class OAuthCredentials(BaseSettings):
    # OAuth 2.0 Google
    google_client_id: str = Field(default='abc')
    google_client_secret: str = Field(default='abc')

    # OAuth 2.0 Google
    yandex_client_id: str = Field(default='abc')
    yandex_client_secret: str = Field(default='abc')

    # OAuth
    facebook_client_secret: str = Field(default='abc')
    facebook_client_id: str = Field(default='abc')

    class Config:
        env_prefix = 'oauth2_'
        env_nested_delimiter = '_'


class Config(BaseSettings):
    """Настройки приложения."""

    app_name: str = Field(default='YP_Auth')
    base_dir: Path = Field(default=Path(__file__).parent)
    flask_env: str = Field(default='development')
    testing: str = Field(default=False)
    debug: str = Field(default=False)

    postgres: DBSettings = DBSettings()

    sqlalchemy_track_modifications: bool = False

    secret_key: str = Field(default='secret_key')
    jwt_secret_key: str = Field(default='jwt_secret_key')

    json_as_ascii: bool = Field(default=False)

    # время жизни access jwt токена в минутах
    access_token_lifetime: int = Field(default=10)

    # время жизни refresh токена в минутах
    refresh_token_lifetime: int = Field(default=14400)

    # алгоритм шифрования JWT-токенов
    jwt_algorithm: str = Field(default="HS256")

    # шаблон формата даты JWT-токена
    jwt_datetime_pattern = "%Y-%m-%d %H:%M:%S"

    # region Redis
    redis: RedisSettings = RedisSettings()

    # endregion

    access_token_type: str = Field(default="access")
    refresh_token_type: str = Field(default="refresh")

    # возможные роли пользователя в сервисе
    admin_role_name: str = Field(default="admin")
    user_role_name: str = Field(default="user")
    subscriber_role_name: str = Field(default="subscriber")

    possible_role_names: list

    rate_limit_threshold_annon_per_minute: int = Field(default=30)
    rate_limit_threshold_registered_per_minute: int = Field(default=50)

    oauth2: OAuthCredentials = OAuthCredentials()

    jaeger_host: str = Field(default="auth_jaeger")
    jaeger_port: int = Field(default=9411)
    jaeger_udp: int = Field(default=6831)

    telemetry_enabled: bool = Field(default=True)

    class Config:
        env_nested_delimiter = '_'

    @root_validator(pre=True)
    def generate(cls, values):
        if values.get('POSSIBLE_ROLE_NAMES') is None:
            values['possible_role_names'] = [
                values.get('admin_role_name'), values.get('user_role_name'), values.get('subscriber_role_name')
            ]
        return values


class ProductionConfig(Config):
    """Конфиг для продакшена."""

    wsgi_host: str = Field(default="0.0.0.0")
    wsgi_port: int = Field(default=8000)


class TestingConfig(Config):
    """Конфиг для тестов."""

    testing: bool = Field(default=True)
    postgres: DBSettingsTest = DBSettingsTest()
    redis_db: str = Field(default='1')


class DevelopmentConfig(Config):
    """Конфиг для девелопмент версии."""
    debug: bool = Field(default=True)


environment = os.environ.get("FLASK_ENV")


if environment == "production":
    app_config = ProductionConfig()
elif environment == "testing":
    app_config = TestingConfig()
else:
    app_config = DevelopmentConfig()


if __name__ == '__main__':
    from pprint import pprint
    pprint(TestingConfig().dict())