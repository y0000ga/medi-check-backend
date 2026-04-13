from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from app.core.datetime import require_utc_datetime
from app.core.enums.history import HistorySource, HistoryStatus
from app.models import History
from app.repositories.history import (
    create_history,
    get_history_by_schedule_occurrence,
)
from app.repositories.medication import get_medication_by_id
from app.repositories.schedule import list_schedule_job_candidates
from app.services.schedule import list_schedule_occurrences_in_range
from app.services.transactions import db_transaction

DEFAULT_MISSED_GRACE_PERIOD = timedelta(hours=2)


def create_missed_histories(
    *,
    db: Session,
    from_datetime: datetime,
    to_datetime: datetime | None = None,
    grace_period: timedelta = DEFAULT_MISSED_GRACE_PERIOD,
) -> int:
    to_datetime = to_datetime or datetime.now(UTC)
    normalized_from_datetime = require_utc_datetime(from_datetime)
    normalized_to_datetime = require_utc_datetime(to_datetime)

    if normalized_to_datetime < normalized_from_datetime:
        return 0

    due_datetime = normalized_to_datetime - grace_period
    if due_datetime < normalized_from_datetime:
        return 0

    schedules = list_schedule_job_candidates(
        db=db,
        from_date=normalized_from_datetime.date(),
        to_date=due_datetime.date(),
    )
    created_count = 0

    with db_transaction(db):
        for schedule in schedules:
            medication = get_medication_by_id(
                db=db,
                medication_id=schedule.medication_id,
            )
            if medication is None:
                continue

            schedule_timezone = ZoneInfo(schedule.timezone)
            scheduled_times = list_schedule_occurrences_in_range(
                schedule=schedule,
                from_datetime=normalized_from_datetime.astimezone(schedule_timezone),
                to_datetime=due_datetime.astimezone(schedule_timezone),
            )

            for scheduled_at in scheduled_times:
                scheduled_at_utc = require_utc_datetime(scheduled_at)
                existing_history = get_history_by_schedule_occurrence(
                    db=db,
                    schedule_id=schedule.id,
                    scheduled_at=scheduled_at_utc,
                )
                if existing_history is not None:
                    continue

                create_history(
                    db=db,
                    history=History(
                        patient_id=schedule.patient_id,
                        schedule_id=schedule.id,
                        medication_id=medication.id,
                        amount_snapshot=schedule.amount,
                        dose_unit_snapshot=schedule.dose_unit,
                        scheduled_at_snapshot=scheduled_at_utc,
                        intake_at=None,
                        status=HistoryStatus.missed,
                        taken_amount=None,
                        memo=None,
                        feeling=None,
                        source=HistorySource.system,
                        medication_name_snapshot=medication.name,
                        medication_dosage_form_snapshot=medication.dosage_form,
                    ),
                )
                created_count += 1

    return created_count
