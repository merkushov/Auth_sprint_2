from pydantic import BaseSettings


class DBSettings(BaseSettings):
    HOST: str = "yp_auth_db"
    PORT: str = "5432"
    DB: str = "users"
    USER: str = "key_keeper"
    PASSWORD: str = "key_keeper"

    class Config:
        env_prefix = "POSTGRES_"

    @property
    def get_url(self):
        return f"postgresql://{self.USER}:{self.PASSWORD}@" f"{self.HOST}/{self.DB}"


class CommonSettings(BaseSettings):
    PROJECT_NAME: str = "auth_api"

    # SERVICE_URL: str = "http://127.0.0.1:5000"

    # для предпродакшн тестов
    SERVICE_URL: str = "http://0.0.0.0:8000"

    # DB: DBSettings = DBSettings()


settings = CommonSettings()
