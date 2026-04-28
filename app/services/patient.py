from sqlalchemy.orm import Session

from app.core.datetime import ensure_utc_datetime
from app.core.enums.care_relationship import PermissionLevel
from app.core.validators import (
    validate_optional_string_field,
    validate_required_string_field,
)
from app.repositories.care_relationship import add_care_relationship
from app.repositories.patient import (
    count_patients,
    create_patient,
    get_patient_detail_row,
    list_patient_options,
    list_patients,
    update_patient as update_patient_record,
)
from app.schemas.patient import (
    CreatePatientPayload,
    CreatePatientResponse,
    DetailPatientPayload,
    DetailPatientResponse,
    EditPatientPayload,
    EditPatientResponse,
    ListPatientOptionsResponse,
    ListPatientsPayload,
    ListPatientsResponse,
    PatientOptionResponse,
    PatientResponse,
)
from app.services.permissions import ensure_can_read, ensure_can_write
from app.services.errors.patient import patient_not_found_error
from app.services.transactions import db_transaction
from app.services.validators.patient import validate_patient_access
from app.validation.rules import AVATAR_URL_RULE, NAME_RULE
from app.validation.rules import MEMO_RULE


def get_patient_list(payload: ListPatientsPayload, db: Session) -> ListPatientsResponse:
    rows = list_patients(query=payload, db=db)
    total_size = count_patients(query=payload, db=db)

    items = [
        PatientResponse(
            id=patient.id,
            permission_level=permission_level,
            linked_user_id=patient.linked_user_id,
            linked_user_name=linked_user_name,
            avatar_url=patient.avatar_url,
            name=patient.name,
            birth_date=ensure_utc_datetime(patient.birth_date),
            note=patient.note,
        )
        for patient, permission_level, linked_user_name in rows
    ]
    return ListPatientsResponse(
        page=payload.page,
        total_size=total_size,
        list=items,
    )


def get_patient_options(
    payload: ListPatientsPayload, db: Session
) -> ListPatientOptionsResponse:
    rows = list_patient_options(query=payload, db=db)
    items = [
        PatientOptionResponse(
            id=patient.id,
            name=patient.name,
            avatar_url=patient.avatar_url,
            permission_level=permission_level,
        )
        for patient, permission_level, _linked_user_name in rows
    ]
    return ListPatientOptionsResponse(list=items)


def get_patient_detail(
    payload: DetailPatientPayload, db: Session
) -> DetailPatientResponse:
    accessible = validate_patient_access(
        user_id=payload.user_id, patient_id=payload.patient_id, db=db
    )
    ensure_can_read(permission_level=accessible.permission_level)

    row = get_patient_detail_row(db=db, patient_id=payload.patient_id)
    if row is None:
        raise patient_not_found_error()

    patient, linked_user_name = row
    return DetailPatientResponse(
        id=patient.id,
        birth_date=ensure_utc_datetime(patient.birth_date),
        linked_user_id=patient.linked_user_id,
        linked_user_name=linked_user_name,
        name=patient.name,
        avatar_url=patient.avatar_url,
        note=patient.note,
        permission_level=accessible.permission_level,
    )


def add_new_patient(
    payload: CreatePatientPayload, db: Session
) -> CreatePatientResponse:
    normalized_birth_date = ensure_utc_datetime(payload.birth_date)
    normalized_name = validate_required_string_field(
        value=payload.name,
        field_name="name",
        rule=NAME_RULE,
        trim=True,
    )
    normalized_avatar_url = validate_optional_string_field(
        value=payload.avatar_url,
        field_name="avatar_url",
        rule=AVATAR_URL_RULE,
        trim=True,
        empty_as_none=True,
    )
    with db_transaction(db):
        patient = create_patient(
            db,
            name=normalized_name,
            birth_date=normalized_birth_date,
            avatar_url=normalized_avatar_url,
            note=payload.note,
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


def edit_patient(payload: EditPatientPayload, db: Session) -> EditPatientResponse:
    normalized_birth_date = None
    if "birth_date" in payload.model_fields_set:
        normalized_birth_date = ensure_utc_datetime(payload.birth_date)

    normalized_name = None
    if "name" in payload.model_fields_set:
        normalized_name = validate_required_string_field(
            value=payload.name,
            field_name="name",
            rule=NAME_RULE,
            trim=True,
        )

    normalized_avatar_url = None
    if "avatar_url" in payload.model_fields_set:
        normalized_avatar_url = validate_optional_string_field(
            value=payload.avatar_url,
            field_name="avatar_url",
            rule=AVATAR_URL_RULE,
            trim=True,
            empty_as_none=True,
        )

    normalized_note = None
    if "note" in payload.model_fields_set:
        normalized_note = validate_optional_string_field(
            value=payload.note,
            field_name="note",
            rule=MEMO_RULE,
            trim=True,
            empty_as_none=True,
        )

    with db_transaction(db):
        accessible = validate_patient_access(
            user_id=payload.user_id,
            patient_id=payload.patient_id,
            db=db,
        )
        ensure_can_write(permission_level=accessible.permission_level)

        patient = update_patient_record(
            db=db,
            patient_id=payload.patient_id,
            name=normalized_name if "name" in payload.model_fields_set else None,
            birth_date=(
                normalized_birth_date if "birth_date" in payload.model_fields_set else None
            ),
            avatar_url=(
                normalized_avatar_url if "avatar_url" in payload.model_fields_set else None
            ),
            note=normalized_note if "note" in payload.model_fields_set else None,
        )

        if patient is None:
            raise patient_not_found_error()

    db.refresh(patient)
    return EditPatientResponse(id=patient.id)
