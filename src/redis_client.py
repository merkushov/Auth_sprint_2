from flask import Flask
from flask_redis import FlaskRedis
from config import app_config

redis_client = FlaskRedis()

def init_redis(app: Flask) -> FlaskRedis:

    # FlaskRedis requires this to be set
    app.config['REDIS_URL'] = app_config.redis.url()

    redis_client.init_app(
        app=app,
        host=app_config.redis.host,
        port=app_config.redis.port,
        db=app_config.redis.db,
    )

    return redis_client
