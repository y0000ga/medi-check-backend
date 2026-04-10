from sqlalchemy.orm import Session
from app.repositories.patient import get_patient_by_user_id
from app.repositories.care_relationship import (
    count_care_relationships,
    list_care_relationships,
)
from app.schemas.care_relationship import (
    CareRelationshipDirection,
    CareRelationshipResponse,
    ListCareRelationshipPayload,
    ListCareRelationshipResponse,
)


def get_care_relationship_list(
    payload: ListCareRelationshipPayload, db: Session
) -> ListCareRelationshipResponse:
    if payload.direction == CareRelationshipDirection.CAREGIVER:
        self_patient = get_patient_by_user_id(db=db, user_id=payload.user_id)
        payload = payload.model_copy(
            update={"self_patient_id": self_patient.id if self_patient is not None else None}
        )

    items = list_care_relationships(query=payload, db=db)
    total_size = count_care_relationships(query=payload, db=db)
    return ListCareRelationshipResponse(
        page=payload.page,
        total_size=total_size,
        list=[
            CareRelationshipResponse(
                id=relationship.id,
                caregiver_user_id=relationship.caregiver_user_id,
                caregiver_name=caregiver_name,
                created_by_user_id=relationship.created_by_user_id,
                patient_id=relationship.patient_id,
                patient_name=patient_name,
                permission_level=relationship.permission_level,
            )
            for relationship, caregiver_name, patient_name in items
        ],
    )
