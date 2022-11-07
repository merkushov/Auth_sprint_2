from uuid import UUID

import exceptions as exc
from models.api.base import BaseServiceModel
from models.db.auth_model import SocialType


class InputSocialAccount(BaseServiceModel):
    user_id: UUID
    social_id: str
    social_name: SocialType

    class Config:
        custom_exception = exc.ApiSocialAccountValidationException
        use_enum_values = True