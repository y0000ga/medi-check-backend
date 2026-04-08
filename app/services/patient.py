from sqlalchemy.orm import Session

from app.core.enums.care_relationship import PermissionLevel
from app.core.validation_rules import (
    AVATAR_URL_MAX_LENGTH,
    AVATAR_URL_MIN_LENGTH,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
)
from app.core.validators import (
    validate_optional_string_field,
    validate_required_string_field,
)
from app.repositories.care_relationship import add_care_relationship
from app.repositories.patient import count_patients, create_patient, list_patients
from app.repositories.user import get_user_by_email
from app.schemas.patient import (
    CreatePatientPayload,
    CreatePatientResponse,
    DetailPatientPayload,
    DetailPatientResponse,
    ListPatientsPayload,
    ListPatientsResponse,
    PatientResponse,
)
from app.services.errors.patient import patient_email_requires_invitation_error
from app.services.permissions import ensure_can_read
from app.services.transactions import db_transaction
from app.services.validators.patient import validate_patient_access


def get_patient_list(payload: ListPatientsPayload, db: Session) -> ListPatientsResponse:
    rows = list_patients(query=payload, db=db)
    total_size = count_patients(query=payload, db=db)

    items = [
        PatientResponse(
            id=patient.id,
            permission_level=permission_level,
            linked_user_id=patient.linked_user_id,
            avatar_url=patient.avatar_url,
            name=patient.name,
            birth_date=patient.birth_date,
        )
        for patient, permission_level in rows
    ]
    return ListPatientsResponse(
        page=payload.page,
        total_size=total_size,
        list=items,
    )


def get_patient_detail(
    payload: DetailPatientPayload, db: Session
) -> DetailPatientResponse:
    accessible = validate_patient_access(
        user_id=payload.user_id, patient_id=payload.patient_id, db=db
    )
    ensure_can_read(permission_level=accessible.permission_level)

    response = DetailPatientResponse(
        id=accessible.patient.id,
        birth_date=accessible.patient.birth_date,
        linked_user_id=accessible.patient.linked_user_id,
        name=accessible.patient.name,
        avatar_url=accessible.patient.avatar_url,
        permission_level=accessible.permission_level,
    )

    return response


def add_new_patient(
    payload: CreatePatientPayload, db: Session
) -> CreatePatientResponse:
    normalized_name = validate_required_string_field(
        value=payload.name,
        field_name="name",
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
        trim=True,
    )
    normalized_avatar_url = validate_optional_string_field(
        value=payload.avatar_url,
        field_name="avatar_url",
        min_length=AVATAR_URL_MIN_LENGTH,
        max_length=AVATAR_URL_MAX_LENGTH,
        trim=True,
        empty_as_none=True,
    )
    if payload.email is not None:
        existing_user = get_user_by_email(db=db, email=payload.email)
        if existing_user is not None:
            raise patient_email_requires_invitation_error()

    with db_transaction(db):
        patient = create_patient(
            db,
            name=normalized_name,
            birth_date=payload.birth_date,
            avatar_url=normalized_avatar_url,
        )

        add_care_relationship(
            db=db,
            caregiver_user_id=payload.user_id,
            created_by_user_id=payload.user_id,
            patient_id=patient.id,
            invitation_id=None,
            permission_level=PermissionLevel.WRITE,
        )

    db.refresh(patient)
    return CreatePatientResponse(id=patient.id)
