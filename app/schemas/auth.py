import uuid
from pydantic import BaseModel, EmailStr


class AuthBodyBase(BaseModel):
    email: EmailStr
    password: str


class AuthPublicResponse(BaseModel):
    user_id: uuid.UUID
    access_token: str


class AuthServiceResult(AuthPublicResponse):
    refresh_token: str


class SignUpBody(AuthBodyBase):
    name: str


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
