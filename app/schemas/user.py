import uuid

from pydantic import BaseModel, EmailStr
from app.core.enums.user import UserStatus


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    avatar_url: str | None
    is_email_verified: bool
    status: UserStatus


class EditUserMeBody(BaseModel):
    name: str | None = None
    avatar_url: str | None = None


class EditUserResponse(BaseModel):
    id: uuid.UUID
