from flask import Flask
from flask_redis import FlaskRedis

redis_client = FlaskRedis()


def init_black_list_storage(app: Flask) -> None:
    redis_client.init_app(app)

    return None
