import click
from flask import Flask

from config import app_config
from scripts.role import create_role
from scripts.user import create_user, get_user


def init_scripts(app: Flask):
    @app.cli.command("createuser")
    def create_user_command():
        """Создать простого пользователя."""
        create_user(app_config.USER_ROLE_NAME)

    @app.cli.command("createsuperuser")
    def create_admin_command():
        """Создать суперпользователя."""
        create_user(app_config.ADMIN_ROLE_NAME)

    @app.cli.command("createsubscriber")
    def create_subscriber_command():
        """Создать пользователя-подписчика."""
        create_user(app_config.SUBSCRIBER_ROLE_NAME)

    @app.cli.command("createrole")
    @click.argument("name")
    def create_role_command(name):
        """Создать роль в базе данных."""
        create_role(name)

    @app.cli.command("showuser")
    @click.argument("name")
    def get_user_command(name):
        """Найти пользователя по имени."""
        get_user(name)
