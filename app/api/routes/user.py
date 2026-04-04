from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models.user import User
from app.schemas.base import ApiResponse
from app.schemas.user import EditUserMeRequest, EditUserResponse, UserResponse
from app.services.user import edit_me

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me")
def get_user_me(user: User = Depends(get_current_user)) -> ApiResponse[UserResponse]:
    user_me_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        is_email_verified=user.is_email_verified,
        avatar_url=user.avatar_url,
        status=user.status,
    )
    return success_response(user_me_response)


@router.patch("/me")
def edit_user_me(
    request_data: EditUserMeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[EditUserResponse]:
    response = edit_me(payload=request_data, user=user, db=db)
    return success_response(response)
