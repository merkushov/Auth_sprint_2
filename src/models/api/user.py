"""Модели соответствующие приянтой схеме API."""

import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import EmailStr, Field, constr

import exceptions as exc
from models.api.base import BaseServiceModel
from models.api.role import Role


class UserIDBase(BaseServiceModel):
    id: UUID = Field(default_factory=uuid4)


class BaseUser(BaseServiceModel):
    username: constr(max_length=256)
    email: EmailStr
    password: constr(max_length=256)


class InputCreateUser(BaseUser):
    class Config:
        custom_exception = exc.ApiValidationErrorException


class InputUpdateUser(BaseServiceModel):
    id: UUID
    username: Optional[constr(max_length=256)]
    email: Optional[EmailStr]
    password: Optional[constr(max_length=256)]

    class Config:
        custom_exception = exc.ApiUserValidationException


class InputLoginUser(BaseUser):
    email: Optional[EmailStr]

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
