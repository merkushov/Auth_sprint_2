from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def init_db(app: Flask) -> SQLAlchemy:
    """Подключение к БД."""
    db.init_app(app)

    return db


def init_migrate(app: Flask, db: SQLAlchemy) -> Migrate:
    """Накатывание миграций на БД."""
    migrate.init_app(app, db)

    return migrate
