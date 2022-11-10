from typing import Optional
from uuid import UUID

import exceptions as exc
from models.api.base import BaseServiceModel
from enum import Enum


class OAuthProvider(Enum):
    self = 0
    yandex = 1
    google = 2
    facebook = 3


class SocialData(BaseServiceModel):
    social_id: str
    social_name: str

    class Config:
        custom_exception = exc.ApiSocialAccountValidationException


class UserInfo(BaseServiceModel):
    email: str
    login: Optional[str]

    class Config:
        custom_exception = exc.ApiSocialAccountValidationException


class ParsedToken(SocialData):
    user_info: UserInfo


class InputSocialAccount(SocialData):
    user_id: UUID

