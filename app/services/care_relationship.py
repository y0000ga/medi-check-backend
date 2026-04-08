from sqlalchemy.orm import Session
from app.repositories.care_relationship import (
    count_care_relationships,
    list_care_relationships,
)
from app.schemas.care_relationship import (
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
        list=items,
    )
