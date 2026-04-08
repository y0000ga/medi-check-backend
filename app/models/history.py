import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums.history import HistorySource, HistoryStatus
from app.core.enums.medication import DosageForm
from app.core.enums.schedule import DosageUnit
from app.core.validation_rules import (
    MEDICATION_NAME_MAX_LENGTH,
    MEDICATION_NOTE_MAX_LENGTH,
)
from app.db.base import Base


class History(Base):
    __tablename__ = "histories"
    __table_args__ = (
        CheckConstraint(
            "amount_snapshot > 0",
            name="ck_histories_amount_snapshot_positive",
        ),
        CheckConstraint(
            "taken_amount IS NULL OR taken_amount > 0",
            name="ck_histories_taken_amount_positive",
        ),
        CheckConstraint(
            "feeling IS NULL OR (feeling >= 1 AND feeling <= 5)",
            name="ck_histories_feeling_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    # 這筆服藥紀錄是屬於哪位病人。
    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("patients.id"),
        nullable=False,
    )

    # 來源 schedule，可為空，因為手動補登不一定對得到既有排程。
    schedule_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("schedules.id"),
        nullable=True,
    )

    # 來源 medication，可為空，保留手動補登或歷史資料鬆綁空間。
    medication_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("medications.id"),
        nullable=True,
    )

    # 以下是當下排程的 snapshot，避免未來 schedule 被修改後影響歷史紀錄。
    amount_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 以下是當下排程的 snapshot，
    dose_unit_snapshot: Mapped[DosageUnit | None] = mapped_column(
        Enum(DosageUnit),
        nullable=True,
    )

    # 以下是當下排程的 snapshot，原本這次應該服藥的時間點。
    scheduled_at_snapshot: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # 使用者實際紀錄吃藥的時間；如果沒吃或系統補記 missed，會是空值。
    intake_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # 這次紀錄的最終狀態，例如 pending / taken / missed。
    status: Mapped[HistoryStatus] = mapped_column(
        Enum(HistoryStatus),
        nullable=False,
    )

    # 實際服用量，可與原始排程量不同。
    taken_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 使用者對這次服藥留下的補充文字。
    memo: Mapped[str | None] = mapped_column(
        String(MEDICATION_NOTE_MAX_LENGTH),
        nullable=True,
    )

    # 使用者主觀感受評分，先用 1~5。
    feeling: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 這筆紀錄是手動補登、快速勾選，還是系統自動判定產生。
    source: Mapped[HistorySource] = mapped_column(
        Enum(HistorySource),
        nullable=False,
    )

    # 以下是 medication 的 snapshot，避免藥名或劑型被修改後影響歷史顯示。
    medication_name_snapshot: Mapped[str] = mapped_column(
        String(MEDICATION_NAME_MAX_LENGTH),
        nullable=False,
    )

    medication_dosage_form_snapshot: Mapped[DosageForm | None] = mapped_column(
        Enum(DosageForm),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
