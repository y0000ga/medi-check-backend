import uuid

from app.db.base import Base
from app.core.validation_rules import EMAIL_MAX_LENGTH

from datetime import datetime, UTC
from sqlalchemy import Uuid, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.enums.care_invitaion import InvitationStatus, InviteeRole

class CareInvitation(Base):
    __tablename__ = "care_invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    # 發起邀請的人，一定有帳號
    inviter_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )

    # 這筆邀請所屬的病人
    # 如果被邀請者已經有有帳號的話，就可以填進去
    # 被邀請者沒帳號的話，可以先對到 Patient；沒有則為 null
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("patients.id"), nullable=True
    )

    # 被邀請者 email
    invitee_email: Mapped[str] = mapped_column(
        String(EMAIL_MAX_LENGTH), nullable=False, index=True
    )

    # 如果被邀請者已經有帳號，可以先對到 user；沒有則為 null
    invitee_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )

    # 被邀請者接受後，會成為什麼角色
    invitee_role: Mapped[InviteeRole] = mapped_column(
        Enum(InviteeRole), nullable=False
    )

    # 邀請狀態
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
