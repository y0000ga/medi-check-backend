"""refactor schedule started_at to start_date

Revision ID: 3f4c2b9d8e1a
Revises: 7d1c6f60dc2c
Create Date: 2026-04-10 17:30:00.000000

"""

from datetime import datetime, time
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3f4c2b9d8e1a"
down_revision: Union[str, Sequence[str], None] = "7d1c6f60dc2c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    op.add_column("schedules", sa.Column("start_date", sa.Date(), nullable=True))

    schedules = sa.table(
        "schedules",
        sa.column("id", sa.Uuid()),
        sa.column("started_at", sa.DateTime(timezone=True)),
        sa.column("start_date", sa.Date()),
        sa.column("time_slots", sa.JSON()),
    )

    rows = bind.execute(
        sa.select(
            schedules.c.id,
            schedules.c.started_at,
            schedules.c.time_slots,
        )
    ).mappings()

    for row in rows:
        started_at: datetime = row["started_at"]
        time_slots = row["time_slots"] or [started_at.time().replace(tzinfo=None).isoformat()]
        bind.execute(
            schedules.update()
            .where(schedules.c.id == row["id"])
            .values(
                start_date=started_at.date(),
                time_slots=time_slots,
            )
        )

    with op.batch_alter_table("schedules") as batch_op:
        batch_op.alter_column("start_date", existing_type=sa.Date(), nullable=False)
        batch_op.alter_column("time_slots", existing_type=sa.JSON(), nullable=False)
        batch_op.drop_column("started_at")


def downgrade() -> None:
    bind = op.get_bind()

    with op.batch_alter_table("schedules") as batch_op:
        batch_op.add_column(sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))

    schedules = sa.table(
        "schedules",
        sa.column("id", sa.Uuid()),
        sa.column("started_at", sa.DateTime(timezone=True)),
        sa.column("start_date", sa.Date()),
        sa.column("time_slots", sa.JSON()),
    )

    rows = bind.execute(
        sa.select(
            schedules.c.id,
            schedules.c.start_date,
            schedules.c.time_slots,
        )
    ).mappings()

    for row in rows:
        time_slots = row["time_slots"] or ["00:00:00"]
        first_slot = time.fromisoformat(time_slots[0])
        bind.execute(
            schedules.update()
            .where(schedules.c.id == row["id"])
            .values(
                started_at=datetime.combine(row["start_date"], first_slot),
            )
        )

    with op.batch_alter_table("schedules") as batch_op:
        batch_op.alter_column("started_at", existing_type=sa.DateTime(timezone=True), nullable=False)
        batch_op.alter_column("time_slots", existing_type=sa.JSON(), nullable=True)
        batch_op.drop_column("start_date")
