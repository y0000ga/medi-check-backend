import uuid

from app.db.base import Base

from datetime import datetime, UTC
from sqlalchemy import Uuid, ForeignKey, UniqueConstraint, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.enums.care_relationship import PermissionLevel, RelationshipStatus


class CareRelationship(Base):
    __tablename__ = "care_relationships"

    __table_args__ = (
        UniqueConstraint(
            "caregiver_user_id",
            "patient_id",
            name="uq_caregiver_patient",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    # 正式照顧者，一定是有帳號的 user
    caregiver_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )

    # 被照顧的病人 (當邀請被確認後，就會建立 Patient 資料並填進來)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("patients.id"), nullable=False
    )

    # 關係來源邀請，可追溯是哪一筆 invitation 成立的
    invitation_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("care_invitations.id"), nullable=True
    )

    # 照顧者可以怎麼樣對待這個病人的資料
    permission_level: Mapped[PermissionLevel] = mapped_column(
        Enum(PermissionLevel), default=PermissionLevel.READ, nullable=False
    )

    # 照顧與病人的關係 -> 存在或撤銷
    status: Mapped[RelationshipStatus] = mapped_column(
        Enum(RelationshipStatus), default=RelationshipStatus.ACTIVE, nullable=False
    )

    # 測銷關係的時間
    revoked_at: Mapped[datetime | None] = mapped_column(
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

