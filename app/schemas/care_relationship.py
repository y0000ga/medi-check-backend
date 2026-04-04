import uuid

from pydantic import BaseModel

from app.core.enums.care_relationship import PermissionLevel
from app.schemas.base import PaginationRequest, PaginationResponse


class CareRelationshipResponse(BaseModel):
    id: uuid.UUID
    caregiver_user_id: uuid.UUID
    patient_id: uuid.UUID
    permission_level: str

class ListCareRelationshipQuery(PaginationRequest):
    permission_level: PermissionLevel | None = None
    user_id: uuid.UUID


class ListCareRelationshipRequest(ListCareRelationshipQuery):
    pass


class ListCareRelationshipPayload(ListCareRelationshipQuery):
    pass


class ListCareRelationshipResponse(PaginationResponse):
    list: list[CareRelationshipResponse]

class DetailCareRelationshipQuery(BaseModel):
    caregiver_user_id: uuid.UUID
    patient_id: uuid.UUID
