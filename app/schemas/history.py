import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.core.enums.history import HistorySource, HistoryStatus
from app.core.enums.medication import DosageForm
from app.core.enums.schedule import DosageUnit
from app.schemas.base import PaginationRequest, PaginationResponse


class HistoryResponse(BaseModel):
    id: uuid.UUID
    intake_at: datetime | None
    status: HistoryStatus
    taken_amount: int | None
    source: HistorySource = Field(
        description="Where this history came from",
        examples=[HistorySource.quickCheck, HistorySource.manual, HistorySource.system],
    )


class HistoryPatientSnapshot(BaseModel):
    id: uuid.UUID
    name: str


class HistoryMedicationSnapshot(BaseModel):
    id: uuid.UUID | None
    name: str
    dosage_form: DosageForm | None


class HistoryScheduleSnapshot(BaseModel):
    id: uuid.UUID | None
    scheduled_at: datetime
    amount: int
    dose_unit: DosageUnit | None


class HistoryListItemResponse(HistoryResponse):
    patient_snapshot: HistoryPatientSnapshot
    medication_snapshot: HistoryMedicationSnapshot
    schedule_snapshot: HistoryScheduleSnapshot


class HistoryDetailResponse(HistoryListItemResponse):
    memo: str | None
    feeling: int | None


class ListHistoriesQuery(PaginationRequest):
    user_id: uuid.UUID
    patient_ids: list[uuid.UUID] | None
    medication_id: uuid.UUID | None
    status: HistoryStatus | None
    from_date: date | None
    to_date: date | None


class ListHistoriesQueryParams(PaginationRequest):
    medication_id: uuid.UUID | None = None
    status: HistoryStatus | None = None
    from_date: date | None = None
    to_date: date | None = None


class ListHistoriesPayload(ListHistoriesQuery):
    pass


class ListHistoriesResponse(PaginationResponse):
    intaken_size: int
    missed_size: int
    list: list[HistoryListItemResponse]


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
    status: HistoryStatus
    intake_at: datetime | None
    source: HistorySource = Field(
        description="Where this history came from",
        examples=[HistorySource.quickCheck],
    )


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
