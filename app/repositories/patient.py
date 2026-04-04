import uuid
from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session

from app.core.enums.care_relationship import PermissionLevel, RelationshipStatus
from app.models.care_relationship import CareRelationship
from app.models.patient import Patient
from app.repositories.helpers import apply_pagination, apply_sort_order
from app.schemas.patient import ListPatientsQuery


def _get_order_column(query: ListPatientsQuery):
    if query.sort_by == "updated_at":
        return CareRelationship.updated_at
    return CareRelationship.created_at


def _build_list_stmt(query: ListPatientsQuery):
    stmt = (
        # 查詢要回兩個東西：Patient 這整個 ORM 物件，CareRelationship.permission_level 這個欄位值
        # (patient, permission_level)
        select(Patient, CareRelationship.permission_level).join(
            # 把 Patient 跟 CareRelationship 兩張表接起來查，先從 Patient 出發，再去找跟它對得上的 CareRelationship
            CareRelationship,
            # 這筆 relationship 是屬於這個 patient 的
            (CareRelationship.patient_id == Patient.id)
            # 只要目前這個 caregiver 的 relationship
            & (CareRelationship.caregiver_user_id == query.user_id)
            # 只要尚未被撤銷的 relationship
            & (CareRelationship.revoked_at.is_(None))
            & (CareRelationship.status.is_not(RelationshipStatus.REVOKED)),
        )
    )

    return stmt


def create_patient_for_user(db: Session, user_id: uuid.UUID, name: str) -> Patient:
    patient = Patient(
        linked_user_id=user_id,
        name=name,
    )
    db.add(patient)
    db.flush()
    return patient


def get_patient_by_user_id(db: Session, user_id: uuid.UUID) -> Patient | None:
    result = db.execute(select(Patient).where(Patient.linked_user_id == user_id))
    return result.scalar_one_or_none()


def list_patients(
    db: Session, query: ListPatientsQuery
) -> list[Row[tuple[Patient, PermissionLevel]]]:
    stmt = _build_list_stmt(query)
    order_column = _get_order_column(query)
    stmt = apply_sort_order(
        stmt, order_column=order_column, sort_order=query.sort_order
    )
    stmt = apply_pagination(stmt=stmt, page=query.page, page_size=query.page_size)

    result = db.execute(stmt)

    # (patient, permission_level)
    # result.scalars().all() 只取第一個
    # result.all() 取全部
    rows = result.all()
    return list(rows)


def count_patients_list(db: Session, query: ListPatientsQuery) -> int:
    stmt = _build_list_stmt(query)
    # with_only_columns(func.count()) 代表查總數
    # order_by(None) 代表不排序
    stmt = stmt.with_only_columns(func.count()).order_by(None)

    return db.scalar(stmt) or 0
