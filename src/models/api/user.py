"""Модели соответствующие приянтой схеме API."""

import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import EmailStr, Field, constr, root_validator

import exceptions as exc
from models.api.base import BaseServiceModel
from models.api.role import Role
from models.db.auth_model import User as ModelUser
from models.db.auth_model import db
from utils.password import random_password


class UserIDBase(BaseServiceModel):
    id: UUID = Field(default_factory=uuid4)


class BaseUser(BaseServiceModel):
    username: constr(max_length=256) = 'Default username'
    email: EmailStr
    password: constr(max_length=256)


class InputCreateUser(BaseUser):
    class Config:
        custom_exception = exc.ApiValidationErrorException


class InputCreateProviderUser(InputCreateUser):

    @root_validator(pre=True)
    def populate_campaign_id(cls, values):
        if not values.get("username") and not values.get("email"):
            raise ValueError("One of two 'username' or 'email' fields must be specified")

        if not values.get("username"):
            email = values.get("email")
            name = email[0 : email.index("@")]
            # чтобы не пересекались username
            while db.session.query(ModelUser).filter(ModelUser.username==name).one_or_none():
                name += '1'
            values['username'] = name

        elif not values.get("email"):
            values["email"] = values.get("username") + "@localhost"

        if not values.get("password"):
            values["password"] = random_password()

        return values


class InputUpdateUser(BaseServiceModel):
    id: UUID
    username: Optional[constr(max_length=256)]
    email: Optional[EmailStr]
    password: Optional[constr(max_length=256)]

    class Config:
        custom_exception = exc.ApiUserValidationException


class InputLoginUser(BaseUser):
    username: Optional[constr(max_length=256)]
    email: Optional[EmailStr]
    password: Optional[constr(max_length=256)]

    class Config:
        custom_exception = exc.ApiValidationErrorException


class User(BaseServiceModel):
    id: UUID
    username: constr(max_length=256)
    email: EmailStr
    password_hash: Optional[str] = None
    roles: list[Role]

    class Config:
        orm_mode = True


class OutputUser(BaseServiceModel):
    id: UUID
    username: constr(max_length=255)
    email: EmailStr


class AccessHistory(BaseServiceModel):
    user_agent: Optional[str] = None
    datetime: datetime.datetime


class InputUserRole(BaseServiceModel):
    user_id: UUID
    role_id: UUID

    class Config:
        custom_exception = exc.ApiUserRoleValidationException
