from sqlalchemy.orm import Session

from app.core.validation_rules import (
    MEDICATION_NAME_MAX_LENGTH,
    MEDICATION_NAME_MIN_LENGTH,
    MEDICATION_NOTE_MAX_LENGTH,
    MEDICATION_NOTE_MIN_LENGTH,
)
from app.core.validators import (
    validate_optional_string_field,
    validate_required_string_field,
)
from app.repositories.medication import (
    count_medications,
    create_medication,
    delete_medication_by_id,
    list_medications,
)
from app.schemas.medication import (
    CreateMedicationPayload,
    CreateMedicationResponse,
    DeleteMedicationPayload,
    DetailMedicationPayload,
    EditMedicationPayload,
    EditMedicationResponse,
    ListMedicationPayload,
    ListMedicationResponse,
    MedicationDetailResponse,
    MedicationResponse,
)
from app.services.permissions import ensure_can_read, ensure_can_write
from app.services.transactions import db_transaction
from app.services.validators.medication import validate_medication_access
from app.services.validators.patient import validate_patient_access


def get_medication_list(
    payload: ListMedicationPayload, db: Session
) -> ListMedicationResponse:
    access = validate_patient_access(
        db=db, user_id=payload.user_id, patient_id=payload.patient_id
    )
    ensure_can_read(permission_level=access.permission_level)

    rows = list_medications(query=payload, db=db)
    total_size = count_medications(query=payload, db=db)

    items = [
        MedicationResponse(
            id=medication.id,
            dosage_form=medication.dosage_form,
            patient_id=medication.patient_id,
            name=medication.name,
        )
        for medication in rows
    ]

    return ListMedicationResponse(page=payload.page, total_size=total_size, list=items)


def get_medication_detail(
    payload: DetailMedicationPayload, db: Session
) -> MedicationDetailResponse:
    access = validate_medication_access(
        db=db, user_id=payload.user_id, medication_id=payload.medication_id
    )
    ensure_can_read(permission_level=access.permission_level)

    return MedicationDetailResponse(
        id=access.medication.id,
        dosage_form=access.medication.dosage_form,
        patient_id=access.medication.patient_id,
        name=access.medication.name,
        note=access.medication.note,
        permission_level=access.permission_level,
    )


def add_medication(
    payload: CreateMedicationPayload, db: Session
) -> CreateMedicationResponse:
    normalized_name = validate_required_string_field(
        value=payload.name,
        field_name="name",
        min_length=MEDICATION_NAME_MIN_LENGTH,
        max_length=MEDICATION_NAME_MAX_LENGTH,
        trim=True,
    )
    normalized_note = None
    if payload.note is not None:
        normalized_note = validate_optional_string_field(
            value=payload.note,
            field_name="note",
            min_length=MEDICATION_NOTE_MIN_LENGTH,
            max_length=MEDICATION_NOTE_MAX_LENGTH,
            trim=True,
        )

    with db_transaction(db):
        access = validate_patient_access(
            db=db, user_id=payload.user_id, patient_id=payload.patient_id
        )
        ensure_can_write(permission_level=access.permission_level)

        medication = create_medication(
            patient_id=payload.patient_id,
            db=db,
            name=normalized_name,
            note=normalized_note,
            dosage_form=payload.dosage_form,
        )

    db.refresh(medication)
    return CreateMedicationResponse(id=medication.id)


def delete_medication(
    payload: DeleteMedicationPayload,
    db: Session,
) -> None:
    with db_transaction(db):
        access = validate_medication_access(
            db=db,
            user_id=payload.user_id,
            medication_id=payload.medication_id,
        )
        ensure_can_write(permission_level=access.permission_level)

        delete_medication_by_id(db=db, medication_id=access.medication.id)
    return None


def update_medication(
    payload: EditMedicationPayload, db: Session
) -> EditMedicationResponse:
    normalized_name = None
    if payload.name is not None:
        normalized_name = validate_required_string_field(
            value=payload.name,
            field_name="name",
            min_length=MEDICATION_NAME_MIN_LENGTH,
            max_length=MEDICATION_NAME_MAX_LENGTH,
            trim=True,
        )

    normalized_note = None
    if "note" in payload.model_fields_set:
        normalized_note = validate_optional_string_field(
            value=payload.note,
            field_name="note",
            min_length=MEDICATION_NOTE_MIN_LENGTH,
            max_length=MEDICATION_NOTE_MAX_LENGTH,
            trim=True,
        )

    with db_transaction(db):
        access = validate_medication_access(
            db=db,
            user_id=payload.user_id,
            medication_id=payload.medication_id,
        )
        ensure_can_write(permission_level=access.permission_level)

        if normalized_name is not None:
            access.medication.name = normalized_name

        if "note" in payload.model_fields_set:
            access.medication.note = normalized_note or ""

        if payload.dosage_form is not None:
            access.medication.dosage_form = payload.dosage_form

    return EditMedicationResponse(medication_id=payload.medication_id)
