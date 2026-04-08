import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select

from app.core.enums.care_relationship import PermissionLevel, RelationshipStatus
from app.models import CareRelationship
from app.repositories.helpers import apply_pagination, apply_sort_order
from app.schemas.care_relationship import (
    DetailCareRelationshipQuery,
    ListCareRelationshipQuery,
)


def _build_list_stmt(query: ListCareRelationshipQuery):
    stmt = select(CareRelationship).where(
        CareRelationship.caregiver_user_id == query.user_id,
        and_(
            CareRelationship.revoked_at.is_(None),
            CareRelationship.status.is_not(RelationshipStatus.REVOKED),
        ),
    )

    if query.permission_level is not None:
        stmt = stmt.where(CareRelationship.permission_level == query.permission_level)

    return stmt


def _get_order_column(query: ListCareRelationshipQuery):
    if query.sort_by == "updated_at":
        return CareRelationship.updated_at
    if query.sort_by == "permission_level":
        return CareRelationship.permission_level
    return CareRelationship.created_at


def list_care_relationships(
    db: Session,
    query: ListCareRelationshipQuery,
) -> list[CareRelationship]:

    stmt = _build_list_stmt(query)
    order_column = _get_order_column(query)

    stmt = apply_sort_order(
        stmt, order_column=order_column, sort_order=query.sort_order
    )

    stmt = apply_pagination(stmt, page=query.page, page_size=query.page_size)

    result = db.execute(stmt)

    return list(result.scalars().all())


def count_care_relationships(
    db: Session,
    query: ListCareRelationshipQuery,
) -> int:
    stmt = _build_list_stmt(query)
    # with_only_columns(func.count()) 代表查總數
    # order_by(None) 代表不排序
    stmt = stmt.with_only_columns(func.count()).order_by(None)

    return db.scalar(stmt) or 0


def get_active_care_relationship(
    db: Session,
    query: DetailCareRelationshipQuery,
) -> CareRelationship | None:
    return db.scalar(
        select(CareRelationship).where(
            CareRelationship.caregiver_user_id == query.caregiver_user_id,
            CareRelationship.patient_id == query.patient_id,
            and_(
                CareRelationship.revoked_at.is_(None),
                CareRelationship.status.is_not(RelationshipStatus.REVOKED),
            ),
        )
    )


def add_care_relationship(
    db: Session,
    caregiver_user_id: uuid.UUID,
    created_by_user_id: uuid.UUID,
    patient_id: uuid.UUID,
    invitation_id: uuid.UUID | None,
    permission_level: PermissionLevel,
) -> CareRelationship:
    care_relationship = CareRelationship(
        caregiver_user_id=caregiver_user_id,
        created_by_user_id=created_by_user_id,
        patient_id=patient_id,
        invitation_id=invitation_id,
        permission_level=permission_level,
        status=RelationshipStatus.ACTIVE,
    )

    db.add(care_relationship)
    db.flush()
    return care_relationship


