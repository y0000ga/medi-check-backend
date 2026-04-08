import uuid

from pydantic import BaseModel

from app.core.enums.care_relationship import PermissionLevel
from app.schemas.base import PaginationRequest, PaginationResponse


class CareRelationshipResponse(BaseModel):
    id: uuid.UUID
    caregiver_user_id: uuid.UUID
    created_by_user_id: uuid.UUID
    patient_id: uuid.UUID
    permission_level: PermissionLevel


class ListCareRelationshipQuery(PaginationRequest):
    permission_level: PermissionLevel | None = None
    user_id: uuid.UUID


class ListCareRelationshipQueryParams(PaginationRequest):
    permission_level: PermissionLevel | None = None


class ListCareRelationshipPayload(ListCareRelationshipQuery):
    pass


class ListCareRelationshipResponse(PaginationResponse):
    list: list[CareRelationshipResponse]


class DetailCareRelationshipQuery(BaseModel):
    caregiver_user_id: uuid.UUID
    patient_id: uuid.UUID
