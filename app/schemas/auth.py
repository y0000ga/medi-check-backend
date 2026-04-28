import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from app.validation.rules import NAME_RULE, PASSWORD_RULE
from app.validation.validators import validate_by_rule


class AuthBodyBase(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_by_rule(value, PASSWORD_RULE)


class AuthPublicResponse(BaseModel):
    user_id: uuid.UUID
    access_token: str


class AuthTokenResponse(AuthPublicResponse):
    refresh_token: str


class SignUpBody(AuthBodyBase):
    name: str
    birth_date: datetime | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return validate_by_rule(value, NAME_RULE)


class SignUpPayload(SignUpBody):
    pass


class SignUpServiceResult(AuthTokenResponse):
    pass


class SignUpResponse(AuthTokenResponse):
    pass


class SignInBody(AuthBodyBase):
    pass


class SignInPayload(SignInBody):
    pass


class SignInServiceResult(AuthTokenResponse):
    pass


class SignInResponse(AuthTokenResponse):
    pass


# Refresh


class RefreshPayload(BaseModel):
    refresh_token: str


class RefreshServiceResult(AuthTokenResponse):
    pass


class RefreshResponse(AuthTokenResponse):
    pass


# Log out
class LogoutPayload(BaseModel):
    refresh_token: str
