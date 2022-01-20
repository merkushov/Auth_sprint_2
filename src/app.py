from flask import Flask, Response, jsonify

from api.routes import init_routes
from black_list_storage import init_black_list_storage
from config import Config, app_config
from db import init_db, init_migrate
from exceptions import ApiException
from scripts import init_scripts


def custom_api_exceptions(exc: ApiException) -> Response:
    response = jsonify(exc.to_dict())
    response.status_code = exc.http_status_code

    return response


def create_app(config_obj: Config = app_config):
    app = Flask(__name__)

    app.config.from_object(config_obj)

    init_black_list_storage(app)

    db = init_db(app)
    init_migrate(app, db)

    init_routes(app)

    init_scripts(app)

    app.register_error_handler(ApiException, custom_api_exceptions)

    return app
