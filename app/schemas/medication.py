import uuid

from pydantic import BaseModel

from app.core.enums.care_relationship import PermissionLevel
from app.core.enums.medication import DosageForm
from app.schemas.base import PaginationRequest, PaginationResponse


class MedicationResponse(BaseModel):
    id: uuid.UUID
    dosage_form: DosageForm
    patient_id: uuid.UUID
    name: str


class MedicationDetailResponse(MedicationResponse):
    note: str | None
    permission_level: PermissionLevel


class ListMedicationQuery(PaginationRequest):
    user_id: uuid.UUID
    dosage_form: DosageForm | None
    patient_id: uuid.UUID
    name: str | None


class ListMedicationQueryParams(PaginationRequest):
    dosage_form: DosageForm | None = None
    name: str | None = None


class ListMedicationPayload(ListMedicationQuery):
    pass


class ListMedicationResponse(PaginationResponse):
    list: list[MedicationResponse]


class DetailMedicationPayload(BaseModel):
    user_id: uuid.UUID
    medication_id: uuid.UUID


class CreateMedicationBody(BaseModel):
    dosage_form: DosageForm
    name: str
    note: str | None = None


class CreateMedicationPayload(BaseModel):
    user_id: uuid.UUID
    patient_id: uuid.UUID
    dosage_form: DosageForm
    name: str
    note: str | None


class CreateMedicationResponse(BaseModel):
    id: uuid.UUID


class DeleteMedicationPayload(BaseModel):
    user_id: uuid.UUID
    medication_id: uuid.UUID


class EditMedicationBody(BaseModel):
    dosage_form: DosageForm | None = None
    name: str | None = None
    note: str | None = None


class EditMedicationPayload(EditMedicationBody):
    user_id: uuid.UUID
    medication_id: uuid.UUID


class EditMedicationResponse(BaseModel):
    medication_id: uuid.UUID
