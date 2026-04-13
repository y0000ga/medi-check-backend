from sqlalchemy.orm import Session
from app.core.datetime import ensure_utc_datetime
from app.models import User
from app.repositories.patient import get_patient_by_user_id
from app.schemas.user import EditUserMeBody, EditUserResponse
from app.core.validation_rules import (
    AVATAR_URL_MAX_LENGTH,
    AVATAR_URL_MIN_LENGTH,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
)
from app.core.validators import validate_optional_string_field
from app.services.errors.patient import current_user_patient_not_found_error
from app.services.transactions import db_transaction


def edit_current_user(
    payload: EditUserMeBody, user: User, db: Session
) -> EditUserResponse:
    normalized_birth_date = ensure_utc_datetime(payload.birth_date)
    normalized_name = None
    normalized_avatar_url = None

    if payload.name is not None:
        normalized_name = validate_optional_string_field(
            value=payload.name,
            field_name="name",
            min_length=NAME_MIN_LENGTH,
            max_length=NAME_MAX_LENGTH,
        )

    if payload.avatar_url is not None:
        normalized_avatar_url = validate_optional_string_field(
            value=payload.avatar_url,
            field_name="avatar_url",
            min_length=AVATAR_URL_MIN_LENGTH,
            max_length=AVATAR_URL_MAX_LENGTH,
            empty_as_none=True,
        )

    with db_transaction(db):
        patient = get_patient_by_user_id(db=db, user_id=user.id)

        if not patient:
            raise current_user_patient_not_found_error()

        if normalized_name is not None:
            user.name = normalized_name
            patient.name = normalized_name

        if payload.avatar_url is not None:
            user.avatar_url = normalized_avatar_url
            patient.avatar_url = normalized_avatar_url

        if payload.birth_date is not None:
            user.birth_date = normalized_birth_date
            patient.birth_date = normalized_birth_date

    db.refresh(user)
    return EditUserResponse(id=user.id)
