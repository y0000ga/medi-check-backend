from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.models import User
from app.repositories.patient import get_patient_by_user_id
from app.schemas.base import ApiResponse
from app.schemas.user import EditUserMeBody, EditUserResponse, UserResponse
from app.services.user import edit_current_user

router = APIRouter(prefix="/users", tags=["user"])


@router.get("/me")
def get_user_me(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[UserResponse]:
    patient = get_patient_by_user_id(db=db, user_id=user.id)
    user_me_response = UserResponse(
        id=user.id,
        patient_id=patient.id if patient is not None else None,
        email=user.email,
        name=user.name,
        is_email_verified=user.is_email_verified,
        avatar_url=user.avatar_url,
        status=user.status,
    )
    return success_response(user_me_response)


@router.patch("/me")
def edit_user_me(
    body: EditUserMeBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[EditUserResponse]:
    response = edit_current_user(payload=body, user=user, db=db)
    return success_response(response)
