from sqlalchemy.orm import Session
from app.repositories.care_relationship import (
    count_care_relationships,
    list_care_relationships,
)
from app.schemas.care_relationship import (
    CareRelationshipResponse,
    ListCareRelationshipPayload,
    ListCareRelationshipResponse,
)


def get_care_relationship_list(
    payload: ListCareRelationshipPayload, db: Session
) -> ListCareRelationshipResponse:
    items = list_care_relationships(query=payload, db=db)
    total_size = count_care_relationships(query=payload, db=db)
    return ListCareRelationshipResponse(
        page=payload.page,
        total_size=total_size,
        list=[
            CareRelationshipResponse(
                id=item.id,
                caregiver_user_id=item.caregiver_user_id,
                created_by_user_id=item.created_by_user_id,
                patient_id=item.patient_id,
                permission_level=item.permission_level,
            )
            for item in items
        ],
    )
