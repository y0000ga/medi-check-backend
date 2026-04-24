import uuid
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


class AuthServiceResult(AuthPublicResponse):
    refresh_token: str


class SignUpBody(AuthBodyBase):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return validate_by_rule(value, NAME_RULE)


class SignUpPayload(SignUpBody):
    pass


class SignUpServiceResult(AuthServiceResult):
    pass


class SignUpResponse(AuthPublicResponse):
    pass


class SignInBody(AuthBodyBase):
    pass


class SignInPayload(SignInBody):
    pass


class SignInServiceResult(AuthServiceResult):
    pass


class SignInResponse(AuthPublicResponse):
    pass


# Refresh


class RefreshPayload(BaseModel):
    refresh_token: str


class RefreshServiceResult(AuthServiceResult):
    pass


class RefreshResponse(AuthPublicResponse):
    pass


# Log out
class LogoutPayload(BaseModel):
    refresh_token: str
