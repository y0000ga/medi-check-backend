from sqlalchemy.orm import Session

from app.repositories.patient import count_patients_list, list_patients
from app.schemas.patient import (
    ListPatientsPayload,
    ListPatientsResponse,
    PatientResponse,
)


def get_patients_list(
    payload: ListPatientsPayload, db: Session
) -> ListPatientsResponse:
    rows = list_patients(query=payload, db=db)
    total_size = count_patients_list(query=payload, db=db)

    items = [
        PatientResponse(
            id=patient.id,
            permission_level=permission_level,
            linked_user_id=patient.linked_user_id,
            avatar_url=patient.avatar_url,
            name=patient.name,
        )
        for patient, permission_level in rows
    ]
    return ListPatientsResponse(
        page=payload.page,
        total_size=total_size,
        list=items,
    )
