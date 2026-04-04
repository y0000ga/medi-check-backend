from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.models.user import User
from app.repositories.patient import get_patient_by_user_id
from app.schemas.user import EditUserMeRequest, EditUserResponse
from app.services.validators.base import validate_optional_string_field


def edit_me(payload: EditUserMeRequest, user: User, db: Session) -> EditUserResponse:
    try:
        normalized_name = None
        normalized_avatar_url = None

        if payload.name is not None:
            normalized_name = validate_optional_string_field(
                value=payload.name,
                field_name="name",
                min_length=1,
                max_length=100,
            )

        if payload.avatar_url is not None:
            normalized_avatar_url = validate_optional_string_field(
                value=payload.avatar_url,
                field_name="avatar_url",
                min_length=1,
                empty_as_none=True,
            )

        patient = get_patient_by_user_id(db=db, user_id=user.id)

        if not patient:
            raise AppException(
                status_code=500,
                message="Patient not found for current user",
            )

        if normalized_name is not None:
            user.name = normalized_name
            patient.name = normalized_name

        if payload.avatar_url is not None:
            user.avatar_url = normalized_avatar_url
            patient.avatar_url = normalized_avatar_url

        db.commit()
        db.refresh(user)
        return EditUserResponse(id=user.id)
    except Exception:
        db.rollback()
        raise
