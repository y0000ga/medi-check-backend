import uuid

from sqlalchemy.orm import Session

from app.repositories.care_relationship import get_care_relationship_detail
from app.repositories.patient import get_patient_by_user_id
from app.schemas.care_relationship import DetailCareRelationshipQuery


# 要先確認該 user_id 是否具備檢視該 patient 權限
# 要不是自己的(user_id === linked_user_id) 或有 care_relationship
def validate_patient_access(
    db: Session, user_id: uuid.UUID, patient_id: uuid.UUID
) -> bool:

    existed_patient = get_patient_by_user_id(user_id=user_id, db=db)

    if existed_patient is None:
        return False

    if existed_patient.linked_user_id == user_id:
        return True

    query = DetailCareRelationshipQuery(
        caregiver_user_id=user_id, patient_id=patient_id
    )

    existed_care_relationship = get_care_relationship_detail(db=db, query=query)

    if existed_care_relationship is None:
        return False

    return True
