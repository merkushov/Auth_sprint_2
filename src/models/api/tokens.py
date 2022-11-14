import datetime
from typing import List, Optional

from pydantic import Field

from config import app_config
from exceptions import ApiValidationErrorException
from models.api.base import BaseServiceModel


class InputRefreshToken(BaseServiceModel):
    refresh_token: str

    class Config:
        custom_exception = ApiValidationErrorException


class AccessToken(BaseServiceModel):
    _encoded_token: Optional[str] = None

    jti: str
    type: str = Field(app_config.access_token_type, const=True)
    user_id: str
    user_roles: Optional[List[str]]
    expired: datetime.datetime

    @property
    def encoded_token(self):
        return self._encoded_token

    class Config:
        underscore_attrs_are_private = True


class RefreshToken(BaseServiceModel):
    _encoded_token: Optional[str] = None

    jti: str
    type: str = Field(app_config.refresh_token_type, const=True)
    user_id: str
    expired: datetime.datetime

    @property
    def encoded_token(self):
        return self._encoded_token

    class Config:
        underscore_attrs_are_private = True


class TokenPair(BaseServiceModel):
    _jti: str
    access: AccessToken
    refresh: RefreshToken

    @property
    def jti(self):
        return self._jti

    class Config:
        underscore_attrs_are_private = True
