import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.core.enums.history import HistorySource, HistoryStatus
from app.core.enums.medication import DosageForm
from app.core.enums.schedule import DosageUnit
from app.schemas.base import PaginationRequest, PaginationResponse


class HistoryResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    schedule_id: uuid.UUID | None
    medication_id: uuid.UUID | None
    scheduled_at: datetime
    intake_at: datetime | None
    status: HistoryStatus
    source: HistorySource
    amount_snapshot: int
    dose_unit_snapshot: DosageUnit | None
    taken_amount: int | None
    medication_name_snapshot: str


class HistoryDetailResponse(HistoryResponse):
    memo: str | None
    feeling: int | None
    medication_dosage_form_snapshot: DosageForm | None


class ListHistoriesQuery(PaginationRequest):
    user_id: uuid.UUID
    patient_ids: list[uuid.UUID] | None
    medication_id: uuid.UUID | None
    status: HistoryStatus | None
    from_date: date | None
    to_date: date | None


class ListHistoriesQueryParams(PaginationRequest):
    patient_ids: list[uuid.UUID] | None = None
    medication_id: uuid.UUID | None = None
    status: HistoryStatus | None = None
    from_date: date | None = None
    to_date: date | None = None


class ListHistoriesPayload(ListHistoriesQuery):
    pass


class ListHistoriesResponse(PaginationResponse):
    list: list[HistoryResponse]


class DetailHistoryPayload(BaseModel):
    user_id: uuid.UUID
    history_id: uuid.UUID


class QuickCheckHistoryBody(BaseModel):
    schedule_id: uuid.UUID
    medication_id: uuid.UUID
    scheduled_at: datetime


class QuickCheckHistoryPayload(QuickCheckHistoryBody):
    user_id: uuid.UUID


class QuickCheckHistoryResponse(BaseModel):
    id: uuid.UUID


class EditHistoryBody(BaseModel):
    intake_at: datetime | None = None
    taken_amount: int | None = None
    memo: str | None = None
    feeling: int | None = None


class EditHistoryPayload(EditHistoryBody):
    user_id: uuid.UUID
    history_id: uuid.UUID


class EditHistoryResponse(BaseModel):
    history_id: uuid.UUID
