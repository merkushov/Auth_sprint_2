from flask import Flask, Response, jsonify

from api.routes import init_routes
from auth import init_oauth
from config import Config, app_config
from db import init_db, init_migrate
from exceptions import ApiException
from rate_limit import init_rate_limit
from redis_client import init_redis
from scripts import init_scripts
from telemetry import init_tracer


def custom_api_exceptions(exc: ApiException) -> Response:
    response = jsonify(exc.to_dict())
    response.status_code = exc.http_status_code

    return response


def create_app(config_obj: Config = app_config):
    app = Flask(__name__)

    app.config.from_object(config_obj)
    app.config['SECRET_KEY'] = app_config.secret_key

    redis_client = init_redis(app)

    db = init_db(app)
    init_migrate(app, db)

    init_oauth(app)
    init_routes(app)
    init_scripts(app)

    init_rate_limit(app, redis_client)

    init_tracer(app)

    app.register_error_handler(ApiException, custom_api_exceptions)

    return app
