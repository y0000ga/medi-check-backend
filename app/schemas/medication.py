import uuid

from pydantic import BaseModel

from app.core.enums.medication import DosageForm
from app.schemas.base import PaginationRequest, PaginationResponse


class MedicationResponse(BaseModel):
    id: uuid.UUID
    dosage_form: DosageForm
    patient_id: uuid.UUID
    name: str
    note: str


class ListMedicationQuery(PaginationRequest):
    user_id: uuid.UUID
    dosageForm: DosageForm | None
    patient_id: uuid.UUID
    name: str | None

class ListMedicationRequest(ListMedicationQuery):
    pass

class ListMedicationPayload(ListMedicationQuery):
    pass

class ListMedicationResponse(PaginationResponse):
    list: list[MedicationResponse]