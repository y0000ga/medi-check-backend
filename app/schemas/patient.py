import uuid

from pydantic import BaseModel
from app.core.enums.care_relationship import PermissionLevel
from app.schemas.base import PaginationRequest, PaginationResponse


class PatientResponse(BaseModel):
    id:uuid.UUID
    linked_user_id: uuid.UUID
    name: str
    avatar_url: str | None
    permission_level: PermissionLevel # 來自 care_relationship

class ListPatientsQuery(PaginationRequest):
    user_id: uuid.UUID


class ListPatientsQueryParams(PaginationRequest):
    pass


class ListPatientsPayload(ListPatientsQuery):
    pass


class ListPatientsResponse(PaginationResponse):
    list: list[PatientResponse]
