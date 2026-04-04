from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.repositories.medication import count_medications_list, list_medications
from app.schemas.medication import (
    ListMedicationPayload,
    ListMedicationResponse,
    MedicationResponse,
)
from app.services.validators.patient import validate_patient_access


def get_medication_list(
    payload: ListMedicationPayload, db: Session
) -> ListMedicationResponse:
    is_access = validate_patient_access(
        db=db, user_id=payload.user_id, patient_id=payload.patient_id
    )

    if is_access == False:
        raise AppException(
            status_code=401,
            message="Cannot access Patient",
        )

    rows = list_medications(query=payload, db=db)
    total_size = count_medications_list(query=payload, db=db)

    items = [
        MedicationResponse(
            id=medication.id,
            dosage_form=medication.dosage_form,
            patient_id=medication.patient_id,
            name=medication.name,
            note=medication.note,
        )
        for medication in rows
    ]

    return ListMedicationResponse(page=payload.page, total_size=total_size, list=items)
