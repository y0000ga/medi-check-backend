import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums.history import HistorySource, HistoryStatus
from app.core.enums.medication import DosageForm
from app.core.enums.schedule import DosageUnit
from app.db.base import Base
from app.validation.rules import MEDICATION_NAME_RULE, MEMO_RULE


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

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("patients.id"),
        nullable=False,
    )

    schedule_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("schedules.id"),
        nullable=True,
    )

    medication_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("medications.id"),
        nullable=True,
    )

    amount_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)

    dose_unit_snapshot: Mapped[DosageUnit | None] = mapped_column(
        Enum(DosageUnit),
        nullable=True,
    )

    scheduled_at_snapshot: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    intake_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[HistoryStatus] = mapped_column(
        Enum(HistoryStatus),
        nullable=False,
    )

    source: Mapped[HistorySource] = mapped_column(
        Enum(HistorySource),
        nullable=False,
    )

    taken_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)

    memo: Mapped[str | None] = mapped_column(
        String(MEMO_RULE['max_length']),
        nullable=True,
    )

    feeling: Mapped[int | None] = mapped_column(Integer, nullable=True)

    medication_name_snapshot: Mapped[str] = mapped_column(
        String(MEDICATION_NAME_RULE['max_length']),
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
