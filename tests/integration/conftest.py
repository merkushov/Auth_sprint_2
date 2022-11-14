"""Конфигуратор Интеграционных авто-тестов.

Создаёт тестовго Клиента и настраивает сессию подключения к БД таким
образом, что каждый тест выполняется в транзакции. После выполнения
теста, созданные в тетсе данные откатываются
"""

import json
import os

import alembic.command as alembic_command
import pytest
import sqlalchemy as sa
from alembic.config import Config as AlembicConfig
from flask import Response
from flask_redis import FlaskRedis
from config import app_config

from app import create_app
from config import TestingConfig
from db import init_db, init_migrate

# Доноры используемых подходов:
#   https://github.com/neurostuff/neurostore/blob/master/neurostore/tests/conftest.py
#   https://github.com/eee333/coursework_3/blob/main/tests/conftest.py
#   https://github.com/LaFa777/pytest-examples/blob/master/tests/conftest.py

original_user = dict(
    username="User Name",
    password="nai(3b&l3lkas)k3awkB_jd",
    email="autotest_me@yandex.ru",
)


@pytest.fixture(scope="session")
def app():
    app = create_app(TestingConfig())

    with app.app_context() as ctx:
        ctx.push()

        yield app

        ctx.pop()


@pytest.fixture(scope="session")
def db(app):
    db = init_db(app)

    alembic_location = os.path.join(app_config.base_dir, "migrations")

    cwd = os.getcwd()
    os.chdir(alembic_location)

    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", alembic_location)
    alembic_cfg.set_main_option("sqlalchemy.url", app_config.postgres.uri())

    alembic_command.upgrade(alembic_cfg, "head")

    os.chdir(cwd)

    init_migrate(app, db)
    db.create_all()

    yield db

    db.session.remove()
    # db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """Фикстура создаёт новую сессию БД для теста.

    Изменения произведённые тестом откатываются автоматически
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    session.begin_nested()

    # session is actually a scoped_session
    # for the `after_transaction_end` event, we need a session instance to
    # listen for, hence the `session()` call
    @sa.event.listens_for(session(), "after_transaction_end")
    def resetart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            session.expire_all()
            session.begin_nested()

    db.session = session

    yield session

    session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(app, session):
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_user(client) -> dict:
    """Эту фикстуру нужно вставлять в атрибуты метода этого класса, если нужно,
    чтобы перед выполнением был создан новый тестовый Пользователь."""
    resp: Response = client.post(
        "/api/v1/user",
        data=json.dumps(original_user),
        content_type="application/json",
    )

    yield resp.get_json()


@pytest.fixture
def auth_request(test_user, client) -> dict:
    """Авторизация тестового пользователя.

    Метод возвращает словарь, содержащий параметры (заголовки и тип
    контента) необходимые для выполнения успешного авторизованного
    запроса.
    """

    resp: Response = client.post(
        "/api/v1/login",
        data=json.dumps(
            {
                "username": original_user["username"],
                "password": original_user["password"],
            }
        ),
        content_type="application/json",
    )

    token_pair = resp.get_json()
    access_token = token_pair["access"]

    yield dict(
        headers={"Authorization": f"Bearer {access_token}"},
        content_type="application/json",
    )

@pytest.fixture(scope="class")
async def clear_cache(app):
    redis_client = FlaskRedis()
    redis_client.init_app(app)
    redis_client.flushall()
    yield
    redis_client.flushall()