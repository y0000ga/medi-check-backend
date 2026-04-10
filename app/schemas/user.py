
import uuid

from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.core.enums.user import UserStatus


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


class EditUserResponse(BaseModel):
    id: uuid.UUID
