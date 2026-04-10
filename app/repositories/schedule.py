import uuid
from datetime import date

from sqlalchemy import Row, and_, delete, func, or_, select
from sqlalchemy.orm import Session

from app.core.enums.care_relationship import RelationshipStatus
from app.core.enums.schedule import EndType
from app.models import CareRelationship, Medication, Patient
from app.models.schedule import Schedule
from app.repositories.helpers import apply_pagination, apply_sort_order
from app.schemas.schedule import ListScheduleMatchesPayload, ListSchedulesQuery


def _get_order_column(query: ListSchedulesQuery):
    if query.sort_by == "updated_at":
        return Schedule.updated_at
    if query.sort_by == "start_date":
        return Schedule.start_date
    if query.sort_by == "medication_id":
        return Schedule.medication_id
    return Schedule.created_at


def _build_schedule_list_stmt(query: ListSchedulesQuery | ListScheduleMatchesPayload):
    stmt = (
        select(Schedule, Medication, Patient.name)
        .join(Medication, Medication.id == Schedule.medication_id)
        .join(Patient, Patient.id == Schedule.patient_id)
        .join(CareRelationship, CareRelationship.patient_id == Schedule.patient_id)
        .where(
            CareRelationship.caregiver_user_id == query.user_id,
            CareRelationship.revoked_at.is_(None),
            CareRelationship.status.is_not(RelationshipStatus.REVOKED),
        )
    )

    if query.patient_ids:
        stmt = stmt.where(Schedule.patient_id.in_(query.patient_ids))

    return stmt


def _build_schedule_match_candidate_stmt(query: ListScheduleMatchesPayload):
    stmt = _build_schedule_list_stmt(query).where(
        Schedule.start_date <= query.to_date,
        or_(
            and_(
                Schedule.end_type.is_(None),
                Schedule.start_date >= query.from_date,
            ),
            Schedule.end_type == EndType.never,
            and_(Schedule.end_type == EndType.until, Schedule.until_date >= query.from_date),
            Schedule.end_type == EndType.counts,
        ),
    )

    return stmt


def create_schedule(
    *,
    db: Session,
    schedule: Schedule,
) -> Schedule:
    db.add(schedule)
    db.flush()
    return schedule


def get_schedule_by_id(
    *,
    db: Session,
    schedule_id: uuid.UUID,
) -> Schedule | None:
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def list_schedules(
    *,
    db: Session,
    query: ListSchedulesQuery,
) -> list[Row[tuple[Schedule, Medication, str]]]:
    stmt = _build_schedule_list_stmt(query=query)
    order_column = _get_order_column(query)
    stmt = apply_sort_order(
        stmt=stmt,
        order_column=order_column,
        sort_order=query.sort_order,
    )

    stmt = apply_pagination(stmt=stmt, page=query.page, page_size=query.page_size)

    result = db.execute(stmt)
    return list(result.all())


def count_schedules(
    *,
    db: Session,
    query: ListSchedulesQuery,
) -> int:
    stmt = _build_schedule_list_stmt(query=query)
    stmt = stmt.with_only_columns(func.count()).order_by(None)
    return db.scalar(stmt) or 0


def list_schedule_match_candidates(
    *,
    db: Session,
    query: ListScheduleMatchesPayload,
) -> list[Row[tuple[Schedule, Medication, str]]]:
    stmt = _build_schedule_match_candidate_stmt(query=query)
    result = db.execute(stmt)
    return list(result.all())


def list_schedule_job_candidates(
    *,
    db: Session,
    from_date: date,
    to_date: date,
) -> list[Schedule]:
    stmt = select(Schedule).where(
        Schedule.start_date <= to_date,
        or_(
            and_(
                Schedule.end_type.is_(None),
                Schedule.start_date >= from_date,
            ),
            Schedule.end_type == EndType.never,
            and_(Schedule.end_type == EndType.until, Schedule.until_date >= from_date),
            Schedule.end_type == EndType.counts,
        ),
    )
    result = db.execute(stmt)
    return list(result.scalars().all())


def delete_schedule_by_id(
    *,
    db: Session,
    schedule_id: uuid.UUID,
) -> None:
    db.execute(delete(Schedule).where(Schedule.id == schedule_id))
