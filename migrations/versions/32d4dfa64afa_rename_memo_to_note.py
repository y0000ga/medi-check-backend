"""rename memo to note

Revision ID: 32d4dfa64afa
Revises: 252ff9368fc8
Create Date: 2026-04-26 23:56:21.395064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32d4dfa64afa'
down_revision: Union[str, Sequence[str], None] = '252ff9368fc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("histories", sa.Column("note", sa.String(length=500), nullable=True))
    op.execute("UPDATE histories SET note = memo WHERE memo IS NOT NULL")
    with op.batch_alter_table("histories") as batch_op:
        batch_op.drop_column("memo")

    op.add_column("patients", sa.Column("note", sa.String(length=1000), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("patients", "note")
    op.add_column("histories", sa.Column("memo", sa.VARCHAR(length=500), nullable=True))
    op.execute("UPDATE histories SET memo = note WHERE note IS NOT NULL")
    with op.batch_alter_table("histories") as batch_op:
        batch_op.drop_column("note")
