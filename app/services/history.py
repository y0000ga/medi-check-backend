import uuid
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.datetime import ensure_utc_datetime, require_utc_datetime
from app.core.enums.history import HistorySource, HistoryStatus
from app.core.enums.medication import DosageForm
from app.validation.rules import MEMO_RULE
from app.core.validators import validate_optional_string_field
from app.models import History
from app.repositories.history import (
    count_histories,
    count_histories_by_status,
    create_history,
    get_history_by_id,
    get_history_by_schedule_occurrence,
    list_histories,
)
from app.repositories.schedule import get_schedule_by_id
from app.schemas.history import (
    DetailHistoryPayload,
    EditHistoryPayload,
    EditHistoryResponse,
    HistoryDetailResponse,
    HistoryListItemResponse,
    HistoryMedicationSnapshot,
    HistoryPatientSnapshot,
    HistoryScheduleSnapshot,
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


def _build_history_response(
    *,
    history: History,
    patient_name: str,
    medication_name: str | None,
    medication_dosage_form: DosageForm | None,
) -> HistoryListItemResponse:
    return HistoryListItemResponse(
        id=history.id,
        intake_at=ensure_utc_datetime(history.intake_at),
        status=history.status,
        taken_amount=history.taken_amount,
        source=history.source,
        patient_snapshot=HistoryPatientSnapshot(
            id=history.patient_id,
            name=patient_name,
        ),
        medication_snapshot=HistoryMedicationSnapshot(
            id=history.medication_id,
            name=medication_name or history.medication_name_snapshot,
            dosage_form=medication_dosage_form or history.medication_dosage_form_snapshot,
        ),
        schedule_snapshot=HistoryScheduleSnapshot(
            id=history.schedule_id,
            scheduled_at=require_utc_datetime(history.scheduled_at_snapshot),
            amount=history.amount_snapshot,
            dose_unit=history.dose_unit_snapshot,
        ),
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
    status_counts = count_histories_by_status(db=db, query=payload)

    return ListHistoriesResponse(
        page=payload.page,
        total_size=total_size,
        intaken_size=status_counts.get(HistoryStatus.taken, 0),
        missed_size=status_counts.get(HistoryStatus.missed, 0),
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
        raise history_not_found_error()

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
        intake_at=ensure_utc_datetime(history.intake_at),
        status=history.status,
        taken_amount=history.taken_amount,
        source=history.source,
        patient_snapshot=HistoryPatientSnapshot(
            id=history.patient_id,
            name=patient_access.patient.name,
        ),
        medication_snapshot=HistoryMedicationSnapshot(
            id=history.medication_id,
            name=(
                medication_access.medication.name
                if medication_access is not None
                else history.medication_name_snapshot
            ),
            dosage_form=(
                medication_access.medication.dosage_form
                if medication_access is not None
                else history.medication_dosage_form_snapshot
            ),
        ),
        schedule_snapshot=HistoryScheduleSnapshot(
            id=history.schedule_id,
            scheduled_at=require_utc_datetime(history.scheduled_at_snapshot),
            amount=history.amount_snapshot,
            dose_unit=history.dose_unit_snapshot,
        ),
        note=history.note,
        feeling=history.feeling,
    )


def add_quick_check_history(
    *,
    db: Session,
    payload: QuickCheckHistoryPayload,
) -> QuickCheckHistoryResponse:
    intake_at = datetime.now(UTC)
    status = HistoryStatus.taken

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

        scheduled_at_utc = require_utc_datetime(payload.scheduled_at)
        scheduled_at_in_schedule_timezone = scheduled_at_utc.astimezone(
            ZoneInfo(schedule.timezone)
        )

        if not schedule_has_occurrence_at(
            schedule=schedule,
            scheduled_at=scheduled_at_in_schedule_timezone,
        ):
            raise invalid_quick_check_schedule_event_error()

        existing_history = get_history_by_schedule_occurrence(
            db=db,
            schedule_id=schedule.id,
            scheduled_at=scheduled_at_utc,
        )
        if existing_history is not None:
            raise duplicate_quick_check_history_error()

        history = create_history(
            db=db,
            history=History(
                patient_id=schedule.patient_id,
                schedule_id=schedule.id,
                medication_id=access.medication.id,
                amount_snapshot=schedule.amount,
                dose_unit_snapshot=schedule.dose_unit,
                scheduled_at_snapshot=scheduled_at_utc,
                intake_at=intake_at,
                status=status,
                source=HistorySource.quickCheck,
                taken_amount=schedule.amount,
                note=None,
                feeling=None,
                medication_name_snapshot=access.medication.name,
                medication_dosage_form_snapshot=access.medication.dosage_form,
            ),
        )

    db.refresh(history)
    return QuickCheckHistoryResponse(
        id=history.id,
        status=history.status,
        intake_at=ensure_utc_datetime(history.intake_at),
        source=history.source,
    )


def update_history(
    *,
    db: Session,
    payload: EditHistoryPayload,
) -> EditHistoryResponse:
    normalized_intake_at = None
    if "intake_at" in payload.model_fields_set:
        normalized_intake_at = ensure_utc_datetime(payload.intake_at)

    normalized_note = None
    if "note" in payload.model_fields_set:
        normalized_note = validate_optional_string_field(
            value=payload.note,
            field_name="note",
            rule=MEMO_RULE,
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
            history.intake_at = normalized_intake_at
            history.source = HistorySource.manual

        if "taken_amount" in payload.model_fields_set:
            history.taken_amount = payload.taken_amount

        if "note" in payload.model_fields_set:
            history.note = normalized_note

        if "feeling" in payload.model_fields_set:
            history.feeling = payload.feeling

    return EditHistoryResponse(history_id=payload.history_id)
