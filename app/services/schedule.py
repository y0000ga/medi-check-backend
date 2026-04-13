import uuid
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.datetime import ensure_utc_datetime, require_utc_datetime
from app.core.enums.schedule import EndType, FrequencyUnit
from app.models import History, Schedule
from app.models.medication import Medication
from app.repositories.history import list_histories_by_schedule_ids_and_date_range
from app.repositories.schedule import (
    count_schedules,
    create_schedule,
    delete_schedule_by_id,
    get_schedule_by_id,
    list_schedule_match_candidates,
    list_schedules,
)
from app.schemas.schedule import (
    CreateSchedulePayload,
    CreateScheduleResponse,
    DeleteSchedulePayload,
    DetailSchedulePayload,
    EditSchedulePayload,
    EditScheduleResponse,
    ListScheduleMatchesPayload,
    ListScheduleMatchesResponse,
    ListSchedulesPayload,
    ListSchedulesResponse,
    ScheduleDetailResponse,
    ScheduleEventHistoryResponse,
    ScheduleEventResponse,
)
from app.services.errors.schedule import (
    invalid_schedule_event_date_range_error,
    schedule_not_found_error,
    schedule_event_date_range_too_large_error,
)
from app.services.permissions import ensure_can_read, ensure_can_write
from app.services.transactions import db_transaction
from app.services.validators.medication import validate_medication_access
from app.services.validators.patient import validate_patient_access
from app.services.validators.schedule import validate_create_schedule_rules

MAX_SCHEDULE_EVENT_RANGE_LENGTH_DAYS = 7


def _validate_schedule_event_date_range(
    *,
    from_date: date,
    to_date: date,
) -> None:
    if to_date < from_date:
        raise invalid_schedule_event_date_range_error()

    date_range_length = (to_date - from_date).days + 1
    if date_range_length > MAX_SCHEDULE_EVENT_RANGE_LENGTH_DAYS:
        raise schedule_event_date_range_too_large_error()


def _iter_dates(
    *,
    from_date: date,
    to_date: date,
):
    cursor = from_date
    while cursor <= to_date:
        yield cursor
        cursor += timedelta(days=1)


def _months_between(start_date: date, target_date: date) -> int:
    return (target_date.year - start_date.year) * 12 + target_date.month - start_date.month


def _matches_frequency(
    *,
    schedule: Schedule,
    target_date: date,
) -> bool:
    if schedule.frequency_unit is None:
        return False

    start_date = schedule.start_date
    interval = schedule.interval or 1
    if target_date < start_date:
        return False

    if schedule.frequency_unit == FrequencyUnit.day:
        return (target_date - start_date).days % interval == 0

    if schedule.frequency_unit == FrequencyUnit.week:
        return (
            schedule.weekdays is not None
            and target_date.isoweekday() in schedule.weekdays
            and ((target_date - start_date).days // 7) % interval == 0
        )

    if schedule.frequency_unit == FrequencyUnit.month:
        return (
            target_date.day == start_date.day
            and _months_between(start_date, target_date) % interval == 0
        )

    if schedule.frequency_unit == FrequencyUnit.year:
        return (
            target_date.month == start_date.month
            and target_date.day == start_date.day
            and (target_date.year - start_date.year) % interval == 0
        )

    return False


def _build_schedule_event_datetimes(
    *,
    schedule: Schedule,
    event_date: date,
) -> list[datetime]:
    event_times = [time.fromisoformat(slot) for slot in schedule.time_slots]
    timezone = ZoneInfo(schedule.timezone)

    return [
        datetime.combine(event_date, event_time, tzinfo=timezone)
        for event_time in event_times
    ]


def _count_events_before(
    *,
    schedule: Schedule,
    target_datetime: datetime,
) -> int:
    event_count = 0
    for event_date in _iter_dates(
        from_date=schedule.start_date,
        to_date=target_datetime.date(),
    ):
        if not _matches_frequency(schedule=schedule, target_date=event_date):
            continue

        for scheduled_at in _build_schedule_event_datetimes(
            schedule=schedule,
            event_date=event_date,
        ):
            if scheduled_at < target_datetime:
                event_count += 1

    return event_count


def _schedule_occurs_on_date(
    *,
    schedule: Schedule,
    target_date: date,
) -> bool:
    start_date = schedule.start_date
    if schedule.end_type is None:
        return target_date == start_date

    if target_date < start_date:
        return False

    if schedule.end_type == EndType.until and (
        schedule.until_date is None or target_date > schedule.until_date
    ):
        return False

    return _matches_frequency(schedule=schedule, target_date=target_date)


def _schedule_has_occurrence_in_range(
    *,
    schedule: Schedule,
    from_date: date,
    to_date: date,
) -> bool:
    for event_date in _iter_dates(from_date=from_date, to_date=to_date):
        if not _schedule_occurs_on_date(schedule=schedule, target_date=event_date):
            continue

        for scheduled_at in _build_schedule_event_datetimes(
            schedule=schedule,
            event_date=event_date,
        ):
            if schedule.end_type == EndType.counts:
                base_count = _count_events_before(
                    schedule=schedule,
                    target_datetime=scheduled_at,
                )
                if (
                    schedule.occurrence_count is None
                    or base_count >= schedule.occurrence_count
                ):
                    continue

            return True

    return False


def schedule_has_occurrence_at(
    *,
    schedule: Schedule,
    scheduled_at: datetime,
) -> bool:
    event_date = scheduled_at.date()
    if not _schedule_occurs_on_date(schedule=schedule, target_date=event_date):
        return False

    matching_event_datetimes = _build_schedule_event_datetimes(
        schedule=schedule,
        event_date=event_date,
    )
    if scheduled_at not in matching_event_datetimes:
        return False

    if schedule.end_type != EndType.counts:
        return True

    base_count = _count_events_before(
        schedule=schedule,
        target_datetime=scheduled_at,
    )
    return (
        schedule.occurrence_count is not None
        and base_count < schedule.occurrence_count
    )


def list_schedule_occurrences_in_range(
    *,
    schedule: Schedule,
    from_datetime: datetime,
    to_datetime: datetime,
) -> list[datetime]:
    occurrences: list[datetime] = []

    for event_date in _iter_dates(
        from_date=from_datetime.date(),
        to_date=to_datetime.date(),
    ):
        if not _schedule_occurs_on_date(schedule=schedule, target_date=event_date):
            continue

        for scheduled_at in _build_schedule_event_datetimes(
            schedule=schedule,
            event_date=event_date,
        ):
            if scheduled_at < from_datetime or scheduled_at > to_datetime:
                continue

            if schedule.end_type == EndType.counts:
                base_count = _count_events_before(
                    schedule=schedule,
                    target_datetime=scheduled_at,
                )
                if (
                    schedule.occurrence_count is None
                    or base_count >= schedule.occurrence_count
                ):
                    continue

            occurrences.append(scheduled_at)

    return occurrences


def _build_schedule_detail_response_with_names(
    *,
    schedule: Schedule,
    medication: Medication,
    patient_name: str,
) -> ScheduleDetailResponse:
    return ScheduleDetailResponse(
        medication_dosage_form=medication.dosage_form,
        id=schedule.id,
        patient_id=schedule.patient_id,
        patient_name=patient_name,
        medication_id=schedule.medication_id,
        medication_name=medication.name,
        timezone=schedule.timezone,
        start_date=schedule.start_date,
        time_slots=schedule.time_slots,
        amount=schedule.amount,
        dose_unit=schedule.dose_unit,
        frequency_unit=schedule.frequency_unit,
        interval=schedule.interval,
        weekdays=schedule.weekdays,
        end_type=schedule.end_type,
        until_date=schedule.until_date,
        occurrence_count=schedule.occurrence_count,
    )


def _build_schedule_event_response(
    *,
    schedule: Schedule,
    medication: Medication,
    patient_name: str,
    scheduled_at: datetime,
    history: History | None,
) -> ScheduleEventResponse:
    return ScheduleEventResponse(
        schedule_id=schedule.id,
        patient_id=schedule.patient_id,
        patient_name=patient_name,
        medication_id=schedule.medication_id,
        medication_name=medication.name,
        medication_dosage_form=medication.dosage_form,
        scheduled_at=require_utc_datetime(scheduled_at),
        amount=schedule.amount,
        dose_unit=schedule.dose_unit,
        history=(
            ScheduleEventHistoryResponse(
                id=history.id,
                status=history.status,
                intake_at=ensure_utc_datetime(history.intake_at),
            )
            if history is not None
            else None
        ),
    )


def _ensure_can_read_patient_filters(
    *,
    db: Session,
    user_id: uuid.UUID,
    patient_ids: list[uuid.UUID] | None,
) -> None:
    if not patient_ids:
        return

    for patient_id in patient_ids:
        access = validate_patient_access(
            db=db,
            user_id=user_id,
            patient_id=patient_id,
        )
        ensure_can_read(permission_level=access.permission_level)


def get_schedule_list(
    *,
    db: Session,
    payload: ListSchedulesPayload,
) -> ListSchedulesResponse:
    _ensure_can_read_patient_filters(
        db=db,
        user_id=payload.user_id,
        patient_ids=payload.patient_ids,
    )

    rows = list_schedules(db=db, query=payload)
    total_size = count_schedules(db=db, query=payload)

    return ListSchedulesResponse(
        page=payload.page,
        total_size=total_size,
        list=[
            _build_schedule_detail_response_with_names(
                schedule=schedule,
                medication=medication,
                patient_name=patient_name,
            )
            for schedule, medication, patient_name in rows
        ],
    )


def get_schedule_match_list(
    *,
    db: Session,
    payload: ListScheduleMatchesPayload,
) -> ListScheduleMatchesResponse:
    _ensure_can_read_patient_filters(
        db=db,
        user_id=payload.user_id,
        patient_ids=payload.patient_ids,
    )

    _validate_schedule_event_date_range(
        from_date=payload.from_date,
        to_date=payload.to_date,
    )

    schedules = list_schedule_match_candidates(db=db, query=payload)
    matched_schedules = [
        (schedule, medication, patient_name)
        for schedule, medication, patient_name in schedules
        if _schedule_has_occurrence_in_range(
            schedule=schedule,
            from_date=payload.from_date,
            to_date=payload.to_date,
        )
    ]

    from_datetime = datetime.combine(payload.from_date, time.min)
    to_datetime = datetime.combine(payload.to_date, time.max)
    schedule_ids = [schedule.id for schedule, _, _ in matched_schedules]
    histories = list_histories_by_schedule_ids_and_date_range(
        db=db,
        schedule_ids=schedule_ids,
        from_date=payload.from_date,
        to_date=payload.to_date,
    )
    history_map = {
        (history.schedule_id, history.scheduled_at_snapshot): history
        for history in histories
        if history.schedule_id is not None
    }

    events: list[ScheduleEventResponse] = []
    for schedule, medication, patient_name in matched_schedules:
        occurrences = list_schedule_occurrences_in_range(
            schedule=schedule,
            from_datetime=from_datetime.replace(tzinfo=ZoneInfo(schedule.timezone)),
            to_datetime=to_datetime.replace(tzinfo=ZoneInfo(schedule.timezone)),
        )
        for scheduled_at in occurrences:
            events.append(
                _build_schedule_event_response(
                    schedule=schedule,
                    medication=medication,
                    patient_name=patient_name,
                    scheduled_at=scheduled_at,
                    history=history_map.get((schedule.id, require_utc_datetime(scheduled_at))),
                )
            )

    events.sort(key=lambda event: event.scheduled_at)

    return ListScheduleMatchesResponse(
        from_date=payload.from_date,
        to_date=payload.to_date,
        list=events,
    )


def add_schedule(
    *,
    db: Session,
    payload: CreateSchedulePayload,
) -> CreateScheduleResponse:
    validate_create_schedule_rules(
        time_slots=payload.time_slots,
        interval=payload.interval,
        frequency_unit=payload.frequency_unit,
        weekdays=payload.weekdays,
        end_type=payload.end_type,
        until_date=payload.until_date,
        start_date=payload.start_date,
        occurrence_count=payload.occurrence_count,
    )

    with db_transaction(db):
        access = validate_medication_access(
            db=db,
            user_id=payload.user_id,
            medication_id=payload.medication_id,
        )
        ensure_can_write(permission_level=access.permission_level)

        schedule = create_schedule(
            db=db,
            schedule=Schedule(
                patient_id=access.medication.patient_id,
                medication_id=access.medication.id,
                timezone=payload.timezone,
                start_date=payload.start_date,
                time_slots=payload.time_slots,
                amount=payload.amount,
                dose_unit=payload.dose_unit,
                frequency_unit=payload.frequency_unit,
                interval=payload.interval,
                weekdays=payload.weekdays,
                end_type=payload.end_type,
                until_date=payload.until_date,
                occurrence_count=payload.occurrence_count,
            ),
        )

    db.refresh(schedule)
    return CreateScheduleResponse(id=schedule.id)


def get_schedule_detail(
    *,
    db: Session,
    payload: DetailSchedulePayload,
) -> ScheduleDetailResponse:
    schedule = get_schedule_by_id(db=db, schedule_id=payload.schedule_id)
    if schedule is None:
        raise schedule_not_found_error()

    access = validate_medication_access(
        db=db,
        user_id=payload.user_id,
        medication_id=schedule.medication_id,
    )
    ensure_can_read(permission_level=access.permission_level)

    patient_access = validate_patient_access(
        db=db,
        user_id=payload.user_id,
        patient_id=schedule.patient_id,
    )

    return _build_schedule_detail_response_with_names(
        schedule=schedule,
        medication=access.medication,
        patient_name=patient_access.patient.name,
    )


def update_schedule(
    *,
    db: Session,
    payload: EditSchedulePayload,
) -> EditScheduleResponse:
    validate_create_schedule_rules(
        time_slots=payload.time_slots,
        interval=payload.interval,
        frequency_unit=payload.frequency_unit,
        weekdays=payload.weekdays,
        end_type=payload.end_type,
        until_date=payload.until_date,
        start_date=payload.start_date,
        occurrence_count=payload.occurrence_count,
    )

    with db_transaction(db):
        schedule = get_schedule_by_id(db=db, schedule_id=payload.schedule_id)
        if schedule is None:
            raise schedule_not_found_error()

        access = validate_medication_access(
            db=db,
            user_id=payload.user_id,
            medication_id=schedule.medication_id,
        )
        ensure_can_write(permission_level=access.permission_level)

        schedule.timezone = payload.timezone
        schedule.start_date = payload.start_date
        schedule.time_slots = payload.time_slots
        schedule.amount = payload.amount
        schedule.dose_unit = payload.dose_unit
        schedule.frequency_unit = payload.frequency_unit
        schedule.interval = payload.interval
        schedule.weekdays = payload.weekdays
        schedule.end_type = payload.end_type
        schedule.until_date = payload.until_date
        schedule.occurrence_count = payload.occurrence_count


    return EditScheduleResponse(schedule_id=payload.schedule_id)


def delete_schedule(
    *,
    db: Session,
    payload: DeleteSchedulePayload,
) -> None:
    with db_transaction(db):
        schedule = get_schedule_by_id(db=db, schedule_id=payload.schedule_id)
        if schedule is None:
            raise schedule_not_found_error()

        access = validate_medication_access(
            db=db,
            user_id=payload.user_id,
            medication_id=schedule.medication_id,
        )
        ensure_can_write(permission_level=access.permission_level)

        delete_schedule_by_id(db=db, schedule_id=payload.schedule_id)
