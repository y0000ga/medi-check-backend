import uuid

from app.core.enums.medication import DosageForm
from app.validation.rules import (
    MEDICATION_NAME_RULE,
    MEMO_RULE,
)
from app.db.base import Base

from datetime import datetime, UTC
from sqlalchemy import Uuid, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column


# 藥物資料
class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("patients.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(MEDICATION_NAME_RULE["max_length"]), nullable=False
    )

    # 劑型
    dosage_form: Mapped[DosageForm] = mapped_column(Enum(DosageForm), nullable=False)

    note: Mapped[str] = mapped_column(
        String(MEMO_RULE["max_length"]), nullable=False, default=""
    )

    # 創建時間
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    # 更新時間
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
