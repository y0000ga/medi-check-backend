import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.core.enums.schedule import DosageUnit, EndType, FrequencyUnit
from app.schemas.base import PaginationRequest, PaginationResponse


class CreateScheduleBody(BaseModel):
    timezone: str
    started_at: datetime
    time_slots: list[str] | None = None
    amount: int
    dose_unit: DosageUnit | None = None
    frequency_unit: FrequencyUnit | None = None
    interval: int | None = None
    weekdays: list[int] | None = None
    end_type: EndType | None = None
    until_date: date | None = None
    occurrence_count: int | None = None


class ScheduleDetailResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    medication_id: uuid.UUID
    timezone: str
    started_at: datetime
    time_slots: list[str] | None
    amount: int
    dose_unit: DosageUnit | None
    frequency_unit: FrequencyUnit | None
    interval: int | None
    weekdays: list[int] | None
    end_type: EndType | None
    until_date: date | None
    occurrence_count: int | None


class DetailSchedulePayload(BaseModel):
    user_id: uuid.UUID
    schedule_id: uuid.UUID


class ListSchedulesQuery(PaginationRequest):
    user_id: uuid.UUID
    patient_ids: list[uuid.UUID] | None = None


class ListSchedulesQueryParams(PaginationRequest):
    patient_ids: list[uuid.UUID] | None = None


class ListSchedulesPayload(ListSchedulesQuery):
    pass


class ListSchedulesResponse(PaginationResponse):
    list: list[ScheduleDetailResponse]


class ListScheduleMatchesQuery(BaseModel):
    from_date: date
    to_date: date
    patient_ids: list[uuid.UUID] | None = None


class ListScheduleMatchesQueryParams(BaseModel):
    from_date: date
    to_date: date
    patient_ids: list[uuid.UUID] | None = None


class ListScheduleMatchesPayload(ListScheduleMatchesQuery):
    user_id: uuid.UUID


class ListScheduleMatchesResponse(BaseModel):
    from_date: date
    to_date: date
    list: list[ScheduleDetailResponse]


class CreateSchedulePayload(CreateScheduleBody):
    user_id: uuid.UUID
    medication_id: uuid.UUID


class CreateScheduleResponse(BaseModel):
    id: uuid.UUID


class EditScheduleBody(BaseModel):
    timezone: str | None = None
    started_at: datetime | None = None
    time_slots: list[str] | None = None
    amount: int | None = None
    dose_unit: DosageUnit | None = None
    frequency_unit: FrequencyUnit | None = None
    interval: int | None = None
    weekdays: list[int] | None = None
    end_type: EndType | None = None
    until_date: date | None = None
    occurrence_count: int | None = None


class EditSchedulePayload(EditScheduleBody):
    user_id: uuid.UUID
    schedule_id: uuid.UUID


class EditScheduleResponse(BaseModel):
    schedule_id: uuid.UUID


class DeleteSchedulePayload(BaseModel):
    user_id: uuid.UUID
    schedule_id: uuid.UUID
