import click
from email_validator import EmailSyntaxError, validate_email

from exceptions import ApiUserAlreadyExistsException
from models.api.user import InputCreateUser
from scripts.utils import WeakPassword, check_password_complexity
from services import RoleService, UserService, get_role_service, get_user_service


def _user_name_prompt():
    """Запросить и получить имя пользователя."""
    name = ""

    while not name:
        name = click.prompt("Enter username", type=str, default="")
        if not name:
            click.echo("User name couldn't be empty!!!")

    return name


def _user_email_prompt():
    """Запросить и получить email от пользователя."""
    email_is_valid = False

    while not email_is_valid:
        try:
            validated_email_object = click.prompt(
                "Enter email", type=str, default="", value_proc=validate_email
            )
        except EmailSyntaxError:
            click.echo("Email should be in valid format!!!")
        else:
            email_is_valid = True

    return validated_email_object.email


def _user_password_prompt(ref_password=None):
    """Запрос и поверка пароля.

    :param ref_password: пароль-образец. Если не задан - пароль вводится впервые, иначе
    функция работает в режиме подтверждения ранее введенного пароля.
    """
    password = ""

    prompt_message = "Enter password"

    if ref_password:
        prompt_message = "Confirm password"

    while not password:
        password = click.prompt(prompt_message, type=str, hide_input=True)

        if not ref_password:
            try:
                check_password_complexity(password)
            except WeakPassword:
                if not click.confirm(
                    "Password is weak, use it anyway?",
                    default=False,
                    show_default=True,
                    err=False,
                ):
                    password = ""
        else:
            if password != ref_password:
                click.echo("Password confirmation is incorrect!!!")
                password = ""

    return password


def create_user(
    user_role: str,
    user_service: UserService = get_user_service(),
    role_service: RoleService = get_role_service(),
):
    """Создать пользователя в базе данных.

    :param role_service: сервис, отвечающий за роли
    :param user_role: роль
    :param user_service: сервис, отвечающий за работу с пользователями
    """
    if user_role not in [role.name for role in role_service.all()]:
        click.echo(f"There is no role '{user_role}' in data base!")
        return

    name = _user_name_prompt()
    email = _user_email_prompt()
    password = _user_password_prompt()
    _user_password_prompt(password)

    user = InputCreateUser(username=name, email=email, password=password)

    try:
        user_service.create_user(user)
    except ApiUserAlreadyExistsException:
        click.echo(f"User '{name}' exists already!")
        return

    user_service.set_role(user_role, name)

    click.echo(f"User '{name}' is created with role '{user_role}'")


def get_user(name, user_service: UserService = get_user_service()):
    """Найти пользователя по имени в базе данных.

    :param user_service: сервис, отвечающий за работу с пользователями
    :param name: имя пользователя
    """
    user = user_service.get_user(username=name)

    click.echo(f"{user.username}, {user.roles}")
