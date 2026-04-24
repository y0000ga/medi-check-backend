
import uuid

from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from app.core.enums.user import UserStatus
from app.validation.rules import AVATAR_URL_RULE, NAME_RULE
from app.validation.validators import validate_by_rule


class UserResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID | None
    email: EmailStr
    name: str
    avatar_url: str | None
    is_email_verified: bool
    status: UserStatus


class EditUserMeBody(BaseModel):
    name: str | None = None
    avatar_url: str | None = None
    birth_date: datetime | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_by_rule(value, NAME_RULE)

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_by_rule(value, AVATAR_URL_RULE)


class EditUserResponse(BaseModel):
    id: uuid.UUID
