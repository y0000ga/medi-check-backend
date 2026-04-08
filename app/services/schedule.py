import uuid
from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.core.enums.schedule import EndType, FrequencyUnit
from app.models import Schedule
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
)
from app.services.errors.schedule import (
    invalid_schedule_event_date_range_error,
    schedule_access_denied_error,
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

    start_date = schedule.started_at.date()
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
    event_times = [schedule.started_at.timetz()]
    if schedule.time_slots:
        event_times = [time.fromisoformat(slot) for slot in schedule.time_slots]

    return [
        datetime.combine(event_date, event_time).replace(
            tzinfo=event_time.tzinfo or schedule.started_at.tzinfo
        )
        for event_time in event_times
    ]


def _count_events_before(
    *,
    schedule: Schedule,
    target_datetime: datetime,
) -> int:
    event_count = 0
    for event_date in _iter_dates(
        from_date=schedule.started_at.date(),
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
    start_date = schedule.started_at.date()
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


def _build_schedule_detail_response(schedule: Schedule) -> ScheduleDetailResponse:
    return ScheduleDetailResponse(
        id=schedule.id,
        patient_id=schedule.patient_id,
        medication_id=schedule.medication_id,
        timezone=schedule.timezone,
        started_at=schedule.started_at,
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
        list=[_build_schedule_detail_response(schedule) for schedule in rows],
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
        schedule
        for schedule in schedules
        if _schedule_has_occurrence_in_range(
            schedule=schedule,
            from_date=payload.from_date,
            to_date=payload.to_date,
        )
    ]

    return ListScheduleMatchesResponse(
        from_date=payload.from_date,
        to_date=payload.to_date,
        list=[
            _build_schedule_detail_response(schedule)
            for schedule in matched_schedules
        ],
    )


def add_schedule(
    *,
    db: Session,
    payload: CreateSchedulePayload,
) -> CreateScheduleResponse:
    validate_create_schedule_rules(
        interval=payload.interval,
        frequency_unit=payload.frequency_unit,
        weekdays=payload.weekdays,
        end_type=payload.end_type,
        until_date=payload.until_date,
        started_at=payload.started_at,
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
                started_at=payload.started_at,
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
        raise schedule_access_denied_error()

    access = validate_medication_access(
        db=db,
        user_id=payload.user_id,
        medication_id=schedule.medication_id,
    )
    ensure_can_read(permission_level=access.permission_level)

    return _build_schedule_detail_response(schedule)


def update_schedule(
    *,
    db: Session,
    payload: EditSchedulePayload,
) -> EditScheduleResponse:
    with db_transaction(db):
        schedule = get_schedule_by_id(db=db, schedule_id=payload.schedule_id)
        if schedule is None:
            raise schedule_access_denied_error()

        access = validate_medication_access(
            db=db,
            user_id=payload.user_id,
            medication_id=schedule.medication_id,
        )
        ensure_can_write(permission_level=access.permission_level)

        fields = payload.model_fields_set - {"user_id", "schedule_id"}
        # 要檢視彼此 validation 的時候就要這樣做 (next_*)
        next_started_at = (
            payload.started_at if "started_at" in fields else schedule.started_at
        )
        next_frequency_unit = (
            payload.frequency_unit
            if "frequency_unit" in fields
            else schedule.frequency_unit
        )
        next_interval = payload.interval if "interval" in fields else schedule.interval
        next_weekdays = payload.weekdays if "weekdays" in fields else schedule.weekdays
        next_end_type = payload.end_type if "end_type" in fields else schedule.end_type
        next_until_date = (
            payload.until_date if "until_date" in fields else schedule.until_date
        )
        next_occurrence_count = (
            payload.occurrence_count
            if "occurrence_count" in fields
            else schedule.occurrence_count
        )

        validate_create_schedule_rules(
            interval=next_interval,
            frequency_unit=next_frequency_unit,
            weekdays=next_weekdays,
            end_type=next_end_type,
            until_date=next_until_date,
            started_at=next_started_at,
            occurrence_count=next_occurrence_count,
        )

        for field in fields:
            setattr(schedule, field, getattr(payload, field))

    return EditScheduleResponse(schedule_id=payload.schedule_id)


def delete_schedule(
    *,
    db: Session,
    payload: DeleteSchedulePayload,
) -> None:
    with db_transaction(db):
        schedule = get_schedule_by_id(db=db, schedule_id=payload.schedule_id)
        if schedule is None:
            raise schedule_access_denied_error()

        access = validate_medication_access(
            db=db,
            user_id=payload.user_id,
            medication_id=schedule.medication_id,
        )
        ensure_can_write(permission_level=access.permission_level)

        delete_schedule_by_id(db=db, schedule_id=payload.schedule_id)
