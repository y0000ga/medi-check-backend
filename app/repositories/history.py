import uuid
from datetime import date, datetime

from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session

from app.core.enums.care_relationship import RelationshipStatus
from app.core.enums.medication import DosageForm
from app.models import CareRelationship, History, Medication, Patient
from app.repositories.helpers import apply_pagination, apply_sort_order
from app.schemas.history import ListHistoriesQuery


def _get_order_column(query: ListHistoriesQuery):
    if query.sort_by == "intake_at":
        return History.intake_at
    if query.sort_by == "scheduled_at":
        return History.scheduled_at_snapshot
    if query.sort_by == "status":
        return History.status
    return History.created_at


def _build_history_list_stmt(*, query: ListHistoriesQuery):
    stmt = (
        select(History, Medication.name, Medication.dosage_form, Patient.name)
        .join(Medication, Medication.id == History.medication_id, isouter=True)
        .join(Patient, Patient.id == History.patient_id)
        .join(CareRelationship, CareRelationship.patient_id == History.patient_id)
        .where(
            CareRelationship.caregiver_user_id == query.user_id,
            CareRelationship.revoked_at.is_(None),
            CareRelationship.status.is_not(RelationshipStatus.REVOKED),
        )
    )

    if query.patient_ids:
        stmt = stmt.where(History.patient_id.in_(query.patient_ids))

    if query.medication_id is not None:
        stmt = stmt.where(History.medication_id == query.medication_id)

    if query.status is not None:
        stmt = stmt.where(History.status == query.status)

    if query.from_date is not None:
        stmt = stmt.where(func.date(History.scheduled_at_snapshot) >= query.from_date)

    if query.to_date is not None:
        stmt = stmt.where(func.date(History.scheduled_at_snapshot) <= query.to_date)

    return stmt


def get_history_by_id(
    *,
    db: Session,
    history_id: uuid.UUID,
) -> History | None:
    return db.get(History, history_id)


def create_history(
    *,
    db: Session,
    history: History,
) -> History:
    db.add(history)
    db.flush()
    return history


def get_history_by_schedule_occurrence(
    *,
    db: Session,
    schedule_id: uuid.UUID,
    scheduled_at: datetime,
) -> History | None:
    stmt = select(History).where(
        History.schedule_id == schedule_id,
        History.scheduled_at_snapshot == scheduled_at,
    )
    return db.scalar(stmt)


def list_histories_by_schedule_ids_and_date_range(
    *,
    db: Session,
    schedule_ids: list[uuid.UUID],
    from_date: date,
    to_date: date,
) -> list[History]:
    if not schedule_ids:
        return []

    stmt = select(History).where(
        History.schedule_id.in_(schedule_ids),
        func.date(History.scheduled_at_snapshot) >= from_date,
        func.date(History.scheduled_at_snapshot) <= to_date,
    )
    result = db.execute(stmt)
    return list(result.scalars().all())


def list_histories(
    *,
    db: Session,
    query: ListHistoriesQuery,
) -> list[Row[tuple[History, str | None, DosageForm | None, str]]]:
    stmt = _build_history_list_stmt(query=query)
    order_column = _get_order_column(query)
    stmt = apply_sort_order(
        stmt=stmt,
        order_column=order_column,
        sort_order=query.sort_order,
    )
    stmt = apply_pagination(stmt=stmt, page=query.page, page_size=query.page_size)
    result = db.execute(stmt)
    return list(result.all())


def count_histories(
    *,
    db: Session,
    query: ListHistoriesQuery,
) -> int:
    stmt = _build_history_list_stmt(query=query)
    stmt = stmt.with_only_columns(func.count()).order_by(None)
    return db.scalar(stmt) or 0
