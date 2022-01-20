"""Модели соответствующие приянтой схеме API для Роли."""

from uuid import UUID, uuid4

from pydantic import Field

import exceptions as exc
from models.api.base import BaseServiceModel


class InputRoleID(BaseServiceModel):
    id: UUID

    class Config:
        custom_exception = exc.ApiRoleValidationException


class InputRole(BaseServiceModel):
    name: str = Field(..., min_length=2, max_length=255)

    class Config:
        custom_exception = exc.ApiRoleValidationException


class Role(BaseServiceModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=2, max_length=255)

    class Config:
        orm_mode = True
