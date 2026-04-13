import uuid

from sqlalchemy.orm import Session

from app.repositories.medication import get_medication_by_id
from app.services.access import MedicationAccess
from app.services.errors.medication import medication_not_found_error
from app.services.validators.patient import validate_patient_access


def validate_medication_access(
    db: Session, user_id: uuid.UUID, medication_id: uuid.UUID
) -> MedicationAccess:

    existed_medication = get_medication_by_id(db=db, medication_id=medication_id)

    if existed_medication is None:
        raise medication_not_found_error()

    access = validate_patient_access(
        db=db, user_id=user_id, patient_id=existed_medication.patient_id
    )

    return MedicationAccess(
        medication=existed_medication, permission_level=access.permission_level
    )
