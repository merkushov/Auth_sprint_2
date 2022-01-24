from flask import Flask
from flask_redis import FlaskRedis

redis_client = FlaskRedis()


def init_redis(app: Flask) -> FlaskRedis:
    redis_client.init_app(app)

    return redis_client
