import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums.care_invitaion import InvitationStatus, InvitationType
from app.core.enums.care_relationship import PermissionLevel
from app.core.validation_rules import EMAIL_MAX_LENGTH
from app.db.base import Base


class CareInvitation(Base):
    __tablename__ = "care_invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    inviter_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )

    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("patients.id"), nullable=True
    )

    invitee_email: Mapped[str] = mapped_column(
        String(EMAIL_MAX_LENGTH), nullable=False, index=True
    )

    invitee_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )

    invitation_type: Mapped[InvitationType] = mapped_column(
        Enum(InvitationType), nullable=False
    )

    permission_level: Mapped[PermissionLevel] = mapped_column(
        Enum(PermissionLevel),
        default=PermissionLevel.READ,
        nullable=False,
    )

    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus),
        default=InvitationStatus.PENDING,
        nullable=False,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    declined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    expired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
