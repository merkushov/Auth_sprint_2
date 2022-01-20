import uuid

import click

from exceptions import ApiRoleAlreadyExistsException
from models.api.role import Role
from services import RoleService, get_role_service


def create_role(role_name, role_service: RoleService = get_role_service()):
    """Создать роль в базе данных."""
    role = Role(id=uuid.uuid4(), name=role_name)

    try:
        role_service.create(role)
    except ApiRoleAlreadyExistsException:
        click.echo(f"Role '{role_name}' is already exist!")
