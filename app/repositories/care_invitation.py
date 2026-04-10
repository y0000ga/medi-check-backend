import uuid
from datetime import UTC, datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased

from app.core.enums.care_invitaion import InvitationStatus, InvitationType
from app.core.enums.care_relationship import PermissionLevel
from app.models import CareInvitation, Patient, User
from app.repositories.helpers import apply_pagination, apply_sort_order
from app.repositories.user import get_user_by_email
from app.schemas.care_invitation import ListCareInvitationQuery


def _get_order_column(query: ListCareInvitationQuery):
    if query.sort_by == "status":
        return CareInvitation.status
    if query.sort_by == "sent_at":
        return CareInvitation.sent_at
    if query.sort_by == "invitee_email":
        return CareInvitation.invitee_email
    return CareInvitation.created_at


def _build_list_stmt(*, query: ListCareInvitationQuery):
    invitee_user = aliased(User)
    stmt = (
        select(CareInvitation, User.name, invitee_user.name)
        .join(User, User.id == CareInvitation.inviter_user_id)
        .outerjoin(invitee_user, invitee_user.id == CareInvitation.invitee_user_id)
        .where(
            or_(
                CareInvitation.inviter_user_id == query.user_id,
                CareInvitation.invitee_user_id == query.user_id,
                CareInvitation.invitee_email == query.user_email,
            )
        )
    )

    if query.direction == "sent":
        stmt = stmt.where(CareInvitation.inviter_user_id == query.user_id)

    if query.direction == "received":
        stmt = stmt.where(
            or_(
                CareInvitation.invitee_user_id == query.user_id,
                CareInvitation.invitee_email == query.user_email,
            )
        )
        stmt = stmt.where(CareInvitation.status == InvitationStatus.PENDING)

    if query.status is not None and query.direction != "received":
        stmt = stmt.where(CareInvitation.status == query.status)

    return stmt


def list_care_invitations(
    *,
    db: Session,
    query: ListCareInvitationQuery,
) -> list[tuple[CareInvitation, str, str | None]]:
    stmt = _build_list_stmt(query=query)
    order_column = _get_order_column(query)
    stmt = apply_sort_order(
        stmt=stmt,
        order_column=order_column,
        sort_order=query.sort_order,
    )
    stmt = apply_pagination(stmt=stmt, page=query.page, page_size=query.page_size)
    result = db.execute(stmt)
    return [(row[0], row[1], row[2]) for row in result.all()]


def count_care_invitations(
    *,
    db: Session,
    query: ListCareInvitationQuery,
) -> int:
    stmt = _build_list_stmt(query=query)
    stmt = stmt.with_only_columns(func.count()).order_by(None)
    return db.scalar(stmt) or 0


def get_care_invitation_by_id(
    *,
    db: Session,
    invitation_id: uuid.UUID,
) -> CareInvitation | None:
    return db.get(CareInvitation, invitation_id)


def get_pending_care_invitation(
    *,
    db: Session,
    inviter_user_id: uuid.UUID,
    patient_id: uuid.UUID | None,
    invitee_email: str,
    invitation_type: InvitationType,
) -> CareInvitation | None:
    stmt = select(CareInvitation).where(
        CareInvitation.inviter_user_id == inviter_user_id,
        CareInvitation.invitee_email == invitee_email,
        CareInvitation.invitation_type == invitation_type,
        CareInvitation.status == InvitationStatus.PENDING,
    )
    if patient_id is None:
        stmt = stmt.where(CareInvitation.patient_id.is_(None))
    else:
        stmt = stmt.where(CareInvitation.patient_id == patient_id)
    return db.scalar(stmt)


def get_pending_care_invitation_for_relationship(
    *,
    db: Session,
    caregiver_user_id: uuid.UUID,
    patient_id: uuid.UUID,
) -> CareInvitation | None:
    stmt = (
        select(CareInvitation)
        .outerjoin(
            Patient,
            and_(
                CareInvitation.invitation_type == InvitationType.INVITE_PATIENT,
                Patient.linked_user_id == CareInvitation.invitee_user_id,
            ),
        )
        .where(CareInvitation.status == InvitationStatus.PENDING)
        .where(
            or_(
                and_(
                    CareInvitation.invitation_type == InvitationType.INVITE_PATIENT,
                    CareInvitation.inviter_user_id == caregiver_user_id,
                    Patient.id == patient_id,
                ),
                and_(
                    CareInvitation.invitation_type == InvitationType.INVITE_CAREGIVER,
                    CareInvitation.invitee_user_id == caregiver_user_id,
                    CareInvitation.patient_id == patient_id,
                ),
            )
        )
    )
    return db.scalar(stmt)


def create_care_invitation(
    *,
    db: Session,
    inviter_user_id: uuid.UUID,
    patient_id: uuid.UUID | None,
    invitee_email: str,
    invitation_type: InvitationType,
    permission_level: PermissionLevel,
) -> CareInvitation:
    invitee_user = get_user_by_email(db=db, email=invitee_email)
    invitation = CareInvitation(
        inviter_user_id=inviter_user_id,
        patient_id=patient_id,
        invitee_email=invitee_email,
        invitee_user_id=invitee_user.id if invitee_user is not None else None,
        invitation_type=invitation_type,
        permission_level=permission_level,
        status=InvitationStatus.PENDING,
        sent_at=datetime.now(UTC),
    )
    db.add(invitation)
    db.flush()
    return invitation


def revoke_care_invitation(
    *,
    invitation: CareInvitation,
) -> CareInvitation:
    invitation.status = InvitationStatus.REVOKED
    invitation.revoked_at = datetime.now(UTC)
    return invitation


def decline_care_invitation(
    *,
    invitation: CareInvitation,
) -> CareInvitation:
    invitation.status = InvitationStatus.DECLINED
    invitation.declined_at = datetime.now(UTC)
    return invitation


def accept_care_invitation(
    *,
    invitation: CareInvitation,
) -> CareInvitation:
    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.now(UTC)
    return invitation
