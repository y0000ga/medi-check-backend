import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums.care_relationship import PermissionLevel
from app.schemas.base import PaginationRequest, PaginationResponse


class PatientResponse(BaseModel):
    id: uuid.UUID
    linked_user_id: uuid.UUID | None
    birth_date: datetime | None
    name: str
    avatar_url: str | None
    permission_level: PermissionLevel  # 來自 care_relationship


class DetailPatientPayload(BaseModel):
    patient_id: uuid.UUID
    user_id: uuid.UUID


class DetailPatientResponse(BaseModel):
    id: uuid.UUID
    linked_user_id: uuid.UUID | None
    name: str
    avatar_url: str | None
    birth_date: datetime | None
    permission_level: PermissionLevel  # 來自 care_relationship


class ListPatientsQuery(PaginationRequest):
    user_id: uuid.UUID
    search: str | None = None


class ListPatientsQueryParams(PaginationRequest):
    search: str | None = None


class ListPatientsPayload(ListPatientsQuery):
    pass


class ListPatientsResponse(PaginationResponse):
    list: list[PatientResponse]


class PatientOptionResponse(BaseModel):
    id: uuid.UUID
    name: str
    avatar_url: str | None
    permission_level: PermissionLevel


class ListPatientOptionsResponse(BaseModel):
    list: list[PatientOptionResponse]


class CreatePatientBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    avatar_url: str | None = None
    birth_date: datetime | None = None


class CreatePatientPayload(CreatePatientBody):
    user_id: uuid.UUID


class CreatePatientResponse(BaseModel):
    id: uuid.UUID
