from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select

from app.core.enums.care_relationship import RelationshipStatus
from app.models.care_relationship import CareRelationship
from app.repositories.helpers import apply_pagination, apply_sort_order
from app.schemas.care_relationship import (
    CareRelationshipResponse,
    DetailCareRelationshipQuery,
    ListCareRelationshipQuery,
)


def _build_care_relationship_list_stmt(query: ListCareRelationshipQuery):
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


def _get_care_relationship_order_column(query: ListCareRelationshipQuery):
    if query.sort_by == "updated_at":
        return CareRelationship.updated_at
    if query.sort_by == "permission_level":
        return CareRelationship.permission_level
    return CareRelationship.created_at


def list_care_relationships(
    db: Session,
    query: ListCareRelationshipQuery,
) -> list[CareRelationshipResponse]:

    stmt = _build_care_relationship_list_stmt(query)
    order_column = _get_care_relationship_order_column(query)

    stmt = apply_sort_order(
        stmt, order_column=order_column, sort_order=query.sort_order
    )

    stmt = apply_pagination(stmt, page=query.page, page_size=query.page_size)

    result = db.execute(stmt)

    return list(result.scalars().all())


def count_care_relationship_list(
    db: Session,
    query: ListCareRelationshipQuery,
) -> int:
    stmt = _build_care_relationship_list_stmt(query)
    # with_only_columns(func.count()) 代表查總數
    # order_by(None) 代表不排序
    stmt = stmt.with_only_columns(func.count()).order_by(None)

    return db.scalar(stmt) or 0


def get_care_relationship_detail(
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
