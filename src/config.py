import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    """Настройки приложения."""

    APP_NAME = 'YP_Auth'
    BASE_DIR = Path(__file__).parent
    TESTING = False
    DEBUG = False

    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    JSON_AS_ASCII = False

    # время жизни access jwt токена в минутах
    ACCESS_TOKEN_LIFETIME = 10

    # время жизни refresh токена в минутах
    REFRESH_TOKEN_LIFETIME = 14400

    # алгоритм шифрования JWT-токенов
    JWT_ALGORITHM = "HS256"

    # шаблон формата даты JWT-токена
    JWT_DATETIME_PATTERN = "%Y-%m-%d %H:%M:%S"

    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
    REDIS_DB = 0

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"

    # возможные роли пользователя в сервисе
    ADMIN_ROLE_NAME = "admin"
    USER_ROLE_NAME = "user"
    SUBSCRIBER_ROLE_NAME = "subscriber"

    POSSIBLE_ROLE_NAMES = [ADMIN_ROLE_NAME, USER_ROLE_NAME, SUBSCRIBER_ROLE_NAME]

    RATE_LIMIT_THRESHOLD_ANNON_PER_MINUTE = 30
    RATE_LIMIT_THRESHOLD_REGISTERED_PER_MINUTE = 50


class ProductionConfig(Config):
    """Конфиг для продакшена."""
    JAEGER_HOST = os.environ.get("JAEGER_HOST")
    JAEGER_PORT = int(os.environ.get("JAEGER_PORT"))
    JAEGER_UDP = int(os.environ.get("JAEGER_UDP"))

    WSGI_HOST = os.environ.get("WSGI_HOST")
    WSGI_PORT = int(os.environ.get("WSGI_PORT"))


class TestingConfig(Config):
    """Конфиг для тестов."""

    TESTING = True
    POSTGRES_DB = os.environ.get("POSTGRES_DB_TEST")
    REDIS_DB = 1


class DevelopmentConfig(Config):
    """Конфиг для девелопмент версии."""

    DEBUG = True


environment = os.environ.get("FLASK_ENV")

if environment == "production":
    app_config = ProductionConfig()
elif environment == "testing":
    app_config = TestingConfig()
else:
    app_config = DevelopmentConfig()
