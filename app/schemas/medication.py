import uuid

from pydantic import BaseModel, field_validator

from app.core.enums.care_relationship import PermissionLevel
from app.core.enums.medication import DosageForm
from app.schemas.base import PaginationRequest, PaginationResponse
from app.validation.rules import MEDICATION_NAME_RULE, MEMO_RULE
from app.validation.validators import validate_by_rule


class MedicationResponse(BaseModel):
    id: uuid.UUID
    dosage_form: DosageForm
    patient_id: uuid.UUID
    patient_name: str
    name: str


class MedicationDetailResponse(MedicationResponse):
    note: str | None
    permission_level: PermissionLevel


class ListMedicationQuery(PaginationRequest):
    user_id: uuid.UUID
    dosage_form: DosageForm | None
    patient_ids: list[uuid.UUID] | None = None
    search: str | None


class ListMedicationQueryParams(PaginationRequest):
    dosage_form: DosageForm | None = None
    search: str | None = None


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

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return validate_by_rule(value, MEDICATION_NAME_RULE)

    @field_validator("note")
    @classmethod
    def validate_note(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_by_rule(value, MEMO_RULE)


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

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_by_rule(value, MEDICATION_NAME_RULE)

    @field_validator("note")
    @classmethod
    def validate_note(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_by_rule(value, MEMO_RULE)


class EditMedicationPayload(EditMedicationBody):
    user_id: uuid.UUID
    medication_id: uuid.UUID


class EditMedicationResponse(BaseModel):
    medication_id: uuid.UUID
