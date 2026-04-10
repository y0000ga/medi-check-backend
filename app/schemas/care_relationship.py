import uuid
from enum import StrEnum

from pydantic import BaseModel

from app.core.enums.care_relationship import PermissionLevel
from app.schemas.base import PaginationRequest, PaginationResponse


class CareRelationshipResponse(BaseModel):
    id: uuid.UUID
    caregiver_user_id: uuid.UUID
    caregiver_name: str
    created_by_user_id: uuid.UUID
    patient_id: uuid.UUID
    patient_name: str
    permission_level: PermissionLevel


class CareRelationshipDirection(StrEnum):
    PATIENT = "patient"
    CAREGIVER = "caregiver"


class ListCareRelationshipQuery(PaginationRequest):
    permission_level: PermissionLevel | None = None
    user_id: uuid.UUID
    direction: CareRelationshipDirection | None = None
    self_patient_id: uuid.UUID | None = None


class ListCareRelationshipQueryParams(PaginationRequest):
    permission_level: PermissionLevel | None = None
    direction: CareRelationshipDirection | None = None


class ListCareRelationshipPayload(ListCareRelationshipQuery):
    pass


class ListCareRelationshipResponse(PaginationResponse):
    list: list[CareRelationshipResponse]


class DetailCareRelationshipQuery(BaseModel):
    caregiver_user_id: uuid.UUID
    patient_id: uuid.UUID
