from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import app_config

db = SQLAlchemy()
migrate = Migrate()


def init_db(app: Flask) -> SQLAlchemy:
    """Подключение к БД."""
    app.config['SQLALCHEMY_DATABASE_URI'] = app_config.postgres.uri()
    db.init_app(
        app=app
    )

    return db


def init_migrate(app: Flask, db: SQLAlchemy) -> Migrate:
    """Накатывание миграций на БД."""
    migrate.init_app(app, db)

    return migrate
