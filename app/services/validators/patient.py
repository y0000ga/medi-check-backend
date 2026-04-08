import uuid

from sqlalchemy.orm import Session

from app.core.enums.care_relationship import PermissionLevel
from app.repositories.care_relationship import get_active_care_relationship
from app.repositories.patient import get_patient_by_id
from app.schemas.care_relationship import DetailCareRelationshipQuery
from app.services.access import PatientAccess
from app.services.errors.patient import patient_access_denied_error


def validate_patient_access(
    db: Session, user_id: uuid.UUID, patient_id: uuid.UUID
) -> PatientAccess:
    target_patient = get_patient_by_id(patient_id=patient_id, db=db)

    if target_patient is None:
        raise patient_access_denied_error()

    if target_patient.linked_user_id == user_id:
        return PatientAccess(
            patient=target_patient, permission_level=PermissionLevel.WRITE
        )

    query = DetailCareRelationshipQuery(
        caregiver_user_id=user_id, patient_id=patient_id
    )

    existed_care_relationship = get_active_care_relationship(db=db, query=query)

    if existed_care_relationship is None:
        raise patient_access_denied_error()

    return PatientAccess(
        patient=target_patient,
        permission_level=existed_care_relationship.permission_level,
    )
