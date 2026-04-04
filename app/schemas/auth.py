import uuid
from pydantic import BaseModel, EmailStr


# Common
class AuthRequestBase(BaseModel):
    email: EmailStr
    password: str


class AuthPublicResponse(BaseModel):
    user_id: uuid.UUID
    access_token: str


class AuthServiceResult(AuthPublicResponse):
    refresh_token: str


# Sign up


class SignUpRequest(AuthRequestBase):
    name: str


class SignUpPayload(SignUpRequest):
    pass


class SignUpServiceResult(AuthServiceResult):
    pass


class SignUpResponse(AuthPublicResponse):
    pass


# Sign In
class SignInRequest(AuthRequestBase):
    pass


class SignInPayload(SignInRequest):
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
