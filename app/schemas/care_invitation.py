import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr

from app.core.enums.care_invitaion import InvitationStatus, InvitationType
from app.core.enums.care_relationship import PermissionLevel
from app.schemas.base import PaginationRequest, PaginationResponse


class CareInvitationDirection(StrEnum):
    SENT = "sent"
    RECEIVED = "received"


class CareInvitationResponse(BaseModel):
    id: uuid.UUID
    inviter_user_id: uuid.UUID
    inviter_name: str
    patient_id: uuid.UUID | None
    invitee_email: str
    invitee_user_id: uuid.UUID | None
    invitee_name: str | None
    invitation_type: InvitationType
    permission_level: PermissionLevel
    status: InvitationStatus
    sent_at: datetime | None
    accepted_at: datetime | None
    declined_at: datetime | None
    revoked_at: datetime | None
    expired_at: datetime | None


class ListCareInvitationQuery(PaginationRequest):
    user_id: uuid.UUID
    user_email: EmailStr
    direction: CareInvitationDirection | None = None
    status: InvitationStatus | None = None


class ListCareInvitationQueryParams(PaginationRequest):
    direction: CareInvitationDirection | None = None
    status: InvitationStatus | None = None


class ListCareInvitationPayload(ListCareInvitationQuery):
    pass


class ListCareInvitationResponse(PaginationResponse):
    list: list[CareInvitationResponse]


class CreateCaregiverInvitationBody(BaseModel):
    invitee_email: EmailStr
    permission_level: PermissionLevel


class CreatePatientInvitationBody(BaseModel):
    invitee_email: EmailStr
    permission_level: PermissionLevel


class CreateCareInvitationPayload(BaseModel):
    user_id: uuid.UUID
    patient_id: uuid.UUID | None = None
    invitee_email: EmailStr
    permission_level: PermissionLevel
    invitation_type: InvitationType


class CreateCareInvitationResponse(BaseModel):
    id: uuid.UUID


class RevokeCareInvitationPayload(BaseModel):
    user_id: uuid.UUID
    invitation_id: uuid.UUID


class RevokeCareInvitationResponse(BaseModel):
    id: uuid.UUID


class DeclineCareInvitationPayload(BaseModel):
    user_id: uuid.UUID
    user_email: EmailStr
    invitation_id: uuid.UUID


class DeclineCareInvitationResponse(BaseModel):
    id: uuid.UUID


class AcceptCareInvitationPayload(BaseModel):
    user_id: uuid.UUID
    user_email: EmailStr
    invitation_id: uuid.UUID


class AcceptCareInvitationResponse(BaseModel):
    id: uuid.UUID
