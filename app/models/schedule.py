import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums.schedule import DosageUnit, EndType, FrequencyUnit
from app.db.base import Base


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_schedules_amount_positive"),
        CheckConstraint(
            "interval IS NULL OR interval >= 1",
            name="ck_schedules_interval_positive",
        ),
        CheckConstraint(
            "occurrence_count IS NULL OR occurrence_count >= 1",
            name="ck_schedules_occurrence_count_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("patients.id"), nullable=False
    )

    medication_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("medications.id"), nullable=False
    )

    timezone: Mapped[str] = mapped_column(String(64), nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    time_slots: Mapped[list[str]] = mapped_column(JSON, nullable=False)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    dose_unit: Mapped[DosageUnit | None] = mapped_column(
        Enum(DosageUnit), nullable=True
    )

    frequency_unit: Mapped[FrequencyUnit | None] = mapped_column(
        Enum(FrequencyUnit), nullable=True
    )

    interval: Mapped[int | None] = mapped_column(Integer, nullable=True)

    weekdays: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)

    end_type: Mapped[EndType | None] = mapped_column(Enum(EndType), nullable=True)

    until_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    occurrence_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
