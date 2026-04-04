from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models.user import User
from app.schemas.care_relationship import (
    ListCareRelationshipPayload,
    ListCareRelationshipRequest,
)
from app.services.care_relationship import get_relationship_list

router = APIRouter(prefix="/care-relationship", tags=["auth"])


# 取得照顧關係列表
@router.get("/list")
def get_list(
    request_data: ListCareRelationshipRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = ListCareRelationshipPayload(
        page=request_data.page,
        page_size=request_data.page_size,
        user_id=user.id,
        permission_level=request_data.permission_level,
    )
    response = get_relationship_list(payload=payload, db=db)
    return success_response(response)
