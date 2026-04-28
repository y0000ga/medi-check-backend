import uuid
from datetime import datetime

from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session

from app.core.enums.care_relationship import PermissionLevel, RelationshipStatus
from app.core.validators import validate_optional_string_field
from app.models import CareRelationship, Patient, User
from app.repositories.helpers import apply_pagination, apply_sort_order
from app.schemas.patient import ListPatientsQuery
from app.validation.rules import NAME_RULE


def _get_order_column(query: ListPatientsQuery):
    if query.sort_by == "name":
        return Patient.name
    if query.sort_by == "birth_date":
        return Patient.birth_date
    return CareRelationship.created_at


def _build_list_stmt(query: ListPatientsQuery):
    stmt = (
        select(Patient, CareRelationship.permission_level, User.name)
        .join(
            CareRelationship,
            (CareRelationship.patient_id == Patient.id)
            & (CareRelationship.caregiver_user_id == query.user_id)
            & (CareRelationship.revoked_at.is_(None))
            & (CareRelationship.status.is_not(RelationshipStatus.REVOKED)),
        )
        .outerjoin(User, User.id == Patient.linked_user_id)
    )

    normalized_search = validate_optional_string_field(
        field_name="search",
        value=query.search,
        rule=NAME_RULE,
        trim=True,
        empty_as_none=True,
    )

    if normalized_search is not None:
        stmt = stmt.where(Patient.name.ilike(f"%{normalized_search}%"))

    return stmt


def _build_detail_stmt(patient_id: uuid.UUID):
    return select(Patient, User.name).outerjoin(User, User.id == Patient.linked_user_id).where(
        Patient.id == patient_id
    )


def create_patient(
    db: Session,
    *,
    linked_user_id: uuid.UUID | None = None,
    name: str,
    birth_date: datetime | None,
    avatar_url: str | None,
    note: str | None,
) -> Patient:
    patient = Patient(
        linked_user_id=linked_user_id,
        name=name,
        birth_date=birth_date,
        avatar_url=avatar_url,
        note=note,
    )
    db.add(patient)
    db.flush()
    return patient


def create_patient_for_user(
    db: Session,
    user_id: uuid.UUID,
    name: str,
    birth_date: datetime | None = None,
    avatar_url: str | None = None,
    note: str | None = None,
) -> Patient:
    return create_patient(
        db=db,
        linked_user_id=user_id,
        name=name,
        birth_date=birth_date,
        avatar_url=avatar_url,
        note=note,
    )


def get_patient_by_user_id(db: Session, user_id: uuid.UUID) -> Patient | None:
    result = db.execute(select(Patient).where(Patient.linked_user_id == user_id))
    return result.scalar_one_or_none()


def get_patient_by_id(db: Session, patient_id: uuid.UUID) -> Patient | None:
    result = db.execute(select(Patient).where(Patient.id == patient_id))
    return result.scalar_one_or_none()


def get_patient_detail_row(
    db: Session, patient_id: uuid.UUID
) -> Row[tuple[Patient, str | None]] | None:
    result = db.execute(_build_detail_stmt(patient_id))
    return result.first()


def list_patients(
    db: Session, query: ListPatientsQuery
) -> list[Row[tuple[Patient, PermissionLevel, str | None]]]:
    stmt = _build_list_stmt(query)
    order_column = _get_order_column(query)
    stmt = apply_sort_order(
        stmt, order_column=order_column, sort_order=query.sort_order
    )
    stmt = apply_pagination(stmt=stmt, page=query.page, page_size=query.page_size)
    return list(db.execute(stmt).all())


def list_patient_options(
    db: Session, query: ListPatientsQuery
) -> list[Row[tuple[Patient, PermissionLevel, str | None]]]:
    stmt = _build_list_stmt(query)
    order_column = _get_order_column(query)
    stmt = apply_sort_order(
        stmt, order_column=order_column, sort_order=query.sort_order
    )
    return list(db.execute(stmt).all())


def count_patients(db: Session, query: ListPatientsQuery) -> int:
    stmt = _build_list_stmt(query)
    stmt = stmt.with_only_columns(func.count()).order_by(None)
    return db.scalar(stmt) or 0


def update_patient(
    db: Session,
    *,
    patient_id: uuid.UUID,
    name: str | None = None,
    birth_date: datetime | None = None,
    avatar_url: str | None = None,
    note: str | None = None,
) -> Patient | None:
    patient = get_patient_by_id(db=db, patient_id=patient_id)
    if patient is None:
        return None

    if name is not None:
        patient.name = name
    if birth_date is not None:
        patient.birth_date = birth_date
    if avatar_url is not None:
        patient.avatar_url = avatar_url
    if note is not None:
        patient.note = note

    db.flush()
    return patient
