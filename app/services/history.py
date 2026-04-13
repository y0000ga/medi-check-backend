import uuid
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy.orm import Session

from app.core.enums.history import HistorySource, HistoryStatus
from app.core.enums.medication import DosageForm
from app.core.validation_rules import (
    MEDICATION_NOTE_MAX_LENGTH,
    MEDICATION_NOTE_MIN_LENGTH,
)
from app.core.validators import validate_optional_string_field
from app.models import History
from app.repositories.history import (
    count_histories,
    create_history,
    get_history_by_id,
    list_histories,
)
from app.repositories.schedule import get_schedule_by_id
from app.schemas.history import (
    DetailHistoryPayload,
    EditHistoryPayload,
    EditHistoryResponse,
    HistoryDetailResponse,
    HistoryResponse,
    ListHistoriesPayload,
    ListHistoriesResponse,
    QuickCheckHistoryPayload,
    QuickCheckHistoryResponse,
)
from app.services.access import MedicationAccess
from app.services.errors.history import (
    duplicate_quick_check_history_error,
    history_not_found_error,
    invalid_history_feeling_error,
    invalid_history_taken_amount_error,
    invalid_quick_check_schedule_event_error,
)
from app.services.errors.schedule import schedule_access_denied_error
from app.services.permissions import ensure_can_read, ensure_can_write
from app.services.schedule import schedule_has_occurrence_at
from app.services.transactions import db_transaction
from app.services.validators.medication import validate_medication_access
from app.services.validators.patient import validate_patient_access

HistoryFlow = Literal["quick_check", "manual", "system_missed"]


def _get_history_status_and_source(
    *,
    flow: HistoryFlow,
) -> tuple[HistoryStatus, HistorySource]:
    if flow == "quick_check":
        return HistoryStatus.taken, HistorySource.quickCheck

    if flow == "manual":
        return HistoryStatus.taken, HistorySource.manual

    return HistoryStatus.missed, HistorySource.system


def _build_history_response(
    *,
    history: History,
    patient_name: str,
    medication_name: str | None,
    medication_dosage_form: DosageForm | None,
) -> HistoryResponse:
    return HistoryResponse(
        id=history.id,
        patient_id=history.patient_id,
        patient_name=patient_name,
        schedule_id=history.schedule_id,
        medication_id=history.medication_id,
        medication_name=medication_name or history.medication_name_snapshot,
        medication_dosage_form=(
            medication_dosage_form or history.medication_dosage_form_snapshot
        ),
        scheduled_at=history.scheduled_at_snapshot,
        intake_at=history.intake_at,
        status=history.status,
        source=history.source,
        amount_snapshot=history.amount_snapshot,
        dose_unit_snapshot=history.dose_unit_snapshot,
        taken_amount=history.taken_amount,
        medication_name_snapshot=history.medication_name_snapshot,
    )


def _ensure_can_read_history_filters(
    *,
    db: Session,
    user_id: uuid.UUID,
    patient_ids: list[uuid.UUID] | None,
    medication_id: uuid.UUID | None,
) -> None:
    if patient_ids:
        for patient_id in patient_ids:
            access = validate_patient_access(
                db=db,
                user_id=user_id,
                patient_id=patient_id,
            )
            ensure_can_read(permission_level=access.permission_level)

    if medication_id is not None:
        access = validate_medication_access(
            db=db,
            user_id=user_id,
            medication_id=medication_id,
        )
        ensure_can_read(permission_level=access.permission_level)


def get_history_list(
    *,
    db: Session,
    payload: ListHistoriesPayload,
) -> ListHistoriesResponse:
    _ensure_can_read_history_filters(
        db=db,
        user_id=payload.user_id,
        patient_ids=payload.patient_ids,
        medication_id=payload.medication_id,
    )

    rows = list_histories(db=db, query=payload)
    total_size = count_histories(db=db, query=payload)

    return ListHistoriesResponse(
        page=payload.page,
        total_size=total_size,
        list=[
            _build_history_response(
                history=history,
                medication_name=medication_name,
                medication_dosage_form=medication_dosage_form,
                patient_name=patient_name,
            )
            for history, medication_name, medication_dosage_form, patient_name in rows
        ],
    )


def get_history_detail(
    *,
    db: Session,
    payload: DetailHistoryPayload,
) -> HistoryDetailResponse:
    history = get_history_by_id(db=db, history_id=payload.history_id)
    if history is None:
        raise history_access_denied_error()

    medication_access: MedicationAccess | None = None
    if history.medication_id is not None:
        medication_access = validate_medication_access(
            db=db,
            user_id=payload.user_id,
            medication_id=history.medication_id,
        )
        ensure_can_read(permission_level=medication_access.permission_level)
    else:
        patient_only_access = validate_patient_access(
            db=db,
            user_id=payload.user_id,
            patient_id=history.patient_id,
        )
        ensure_can_read(permission_level=patient_only_access.permission_level)

    patient_access = validate_patient_access(
        db=db,
        user_id=payload.user_id,
        patient_id=history.patient_id,
    )

    return HistoryDetailResponse(
        id=history.id,
        patient_id=history.patient_id,
        patient_name=patient_access.patient.name,
        schedule_id=history.schedule_id,
        medication_id=history.medication_id,
        medication_name=(
            medication_access.medication.name
            if medication_access is not None
            else history.medication_name_snapshot
        ),
        medication_dosage_form=(
            medication_access.medication.dosage_form
            if medication_access is not None
            else history.medication_dosage_form_snapshot
        ),
        scheduled_at=history.scheduled_at_snapshot,
        intake_at=history.intake_at,
        status=history.status,
        source=history.source,
        amount_snapshot=history.amount_snapshot,
        dose_unit_snapshot=history.dose_unit_snapshot,
        taken_amount=history.taken_amount,
        medication_name_snapshot=history.medication_name_snapshot,
        memo=history.memo,
        feeling=history.feeling,
        medication_dosage_form_snapshot=history.medication_dosage_form_snapshot,
    )


def add_quick_check_history(
    *,
    db: Session,
    payload: QuickCheckHistoryPayload,
) -> QuickCheckHistoryResponse:
    intake_at = datetime.now(UTC)
    status, source = _get_history_status_and_source(flow="quick_check")

    with db_transaction(db):
        access = validate_medication_access(
            db=db,
            user_id=payload.user_id,
            medication_id=payload.medication_id,
        )
        ensure_can_write(permission_level=access.permission_level)

        schedule = get_schedule_by_id(db=db, schedule_id=payload.schedule_id)
        if (
            schedule is None
            or schedule.medication_id != access.medication.id
            or schedule.patient_id != access.medication.patient_id
        ):
            raise schedule_access_denied_error()

        if not schedule_has_occurrence_at(
            schedule=schedule,
            scheduled_at=payload.scheduled_at,
        ):
            raise invalid_quick_check_schedule_event_error()

        history = create_history(
            db=db,
            history=History(
                patient_id=schedule.patient_id,
                schedule_id=schedule.id,
                medication_id=access.medication.id,
                amount_snapshot=schedule.amount,
                dose_unit_snapshot=schedule.dose_unit,
                scheduled_at_snapshot=payload.scheduled_at,
                intake_at=intake_at,
                status=status,
                taken_amount=schedule.amount,
                memo=None,
                feeling=None,
                source=source,
                medication_name_snapshot=access.medication.name,
                medication_dosage_form_snapshot=access.medication.dosage_form,
            ),
        )

    db.refresh(history)
    return QuickCheckHistoryResponse(id=history.id)


def update_history(
    *,
    db: Session,
    payload: EditHistoryPayload,
) -> EditHistoryResponse:
    normalized_memo = None
    if "memo" in payload.model_fields_set:
        normalized_memo = validate_optional_string_field(
            value=payload.memo,
            field_name="memo",
            min_length=MEDICATION_NOTE_MIN_LENGTH,
            max_length=MEDICATION_NOTE_MAX_LENGTH,
            trim=True,
            empty_as_none=True,
        )

    if payload.feeling is not None and not 1 <= payload.feeling <= 5:
        raise invalid_history_feeling_error()

    if payload.taken_amount is not None and payload.taken_amount <= 0:
        raise invalid_history_taken_amount_error()

    with db_transaction(db):
        history = get_history_by_id(db=db, history_id=payload.history_id)
        if history is None:
            raise history_not_found_error()

        if history.medication_id is not None:
            access = validate_medication_access(
                db=db,
                user_id=payload.user_id,
                medication_id=history.medication_id,
            )
            ensure_can_write(permission_level=access.permission_level)
        else:
            access = validate_patient_access(
                db=db,
                user_id=payload.user_id,
                patient_id=history.patient_id,
            )
            ensure_can_write(permission_level=access.permission_level)

        if "intake_at" in payload.model_fields_set:
            history.intake_at = payload.intake_at

        if "taken_amount" in payload.model_fields_set:
            history.taken_amount = payload.taken_amount

        if "memo" in payload.model_fields_set:
            history.memo = normalized_memo

        if "feeling" in payload.model_fields_set:
            history.feeling = payload.feeling

    return EditHistoryResponse(history_id=payload.history_id)
