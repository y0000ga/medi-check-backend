"""align dosage enum values

Revision ID: 7b3a2d1c4f90
Revises: 32d4dfa64afa
Create Date: 2026-04-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "7b3a2d1c4f90"
down_revision: Union[str, Sequence[str], None] = "32d4dfa64afa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE medications
        SET dosage_form = CASE dosage_form
            WHEN 'Tablet' THEN 'tablet'
            WHEN 'Capsule' THEN 'capsule'
            WHEN 'Softgel' THEN 'softgel'
            WHEN 'Liquid' THEN 'liquid'
            WHEN 'Powder' THEN 'powder'
            WHEN 'Pill' THEN 'pill'
            WHEN 'Spray' THEN 'spray'
            ELSE dosage_form
        END
        """
    )

    op.execute(
        """
        UPDATE histories
        SET medication_dosage_form_snapshot = CASE medication_dosage_form_snapshot
            WHEN 'Tablet' THEN 'tablet'
            WHEN 'Capsule' THEN 'capsule'
            WHEN 'Softgel' THEN 'softgel'
            WHEN 'Liquid' THEN 'liquid'
            WHEN 'Powder' THEN 'powder'
            WHEN 'Pill' THEN 'pill'
            WHEN 'Spray' THEN 'spray'
            ELSE medication_dosage_form_snapshot
        END
        """
    )

    op.execute(
        """
        UPDATE schedules
        SET dose_unit = CASE dose_unit
            WHEN 'Mg' THEN 'mg'
            WHEN 'Ml' THEN 'ml'
            WHEN 'Tablet' THEN 'tablet'
            WHEN 'Capsule' THEN 'capsule'
            WHEN 'Package' THEN 'packet'
            WHEN 'Drop' THEN 'drop'
            ELSE dose_unit
        END
        """
    )

    op.execute(
        """
        UPDATE histories
        SET dose_unit_snapshot = CASE dose_unit_snapshot
            WHEN 'Mg' THEN 'mg'
            WHEN 'Ml' THEN 'ml'
            WHEN 'Tablet' THEN 'tablet'
            WHEN 'Capsule' THEN 'capsule'
            WHEN 'Package' THEN 'packet'
            WHEN 'Drop' THEN 'drop'
            ELSE dose_unit_snapshot
        END
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE medications
        SET dosage_form = CASE dosage_form
            WHEN 'tablet' THEN 'Tablet'
            WHEN 'capsule' THEN 'Capsule'
            WHEN 'softgel' THEN 'Softgel'
            WHEN 'liquid' THEN 'Liquid'
            WHEN 'powder' THEN 'Powder'
            WHEN 'pill' THEN 'Pill'
            WHEN 'spray' THEN 'Spray'
            ELSE dosage_form
        END
        """
    )

    op.execute(
        """
        UPDATE histories
        SET medication_dosage_form_snapshot = CASE medication_dosage_form_snapshot
            WHEN 'tablet' THEN 'Tablet'
            WHEN 'capsule' THEN 'Capsule'
            WHEN 'softgel' THEN 'Softgel'
            WHEN 'liquid' THEN 'Liquid'
            WHEN 'powder' THEN 'Powder'
            WHEN 'pill' THEN 'Pill'
            WHEN 'spray' THEN 'Spray'
            ELSE medication_dosage_form_snapshot
        END
        """
    )

    op.execute(
        """
        UPDATE schedules
        SET dose_unit = CASE dose_unit
            WHEN 'mg' THEN 'Mg'
            WHEN 'ml' THEN 'Ml'
            WHEN 'tablet' THEN 'Tablet'
            WHEN 'capsule' THEN 'Capsule'
            WHEN 'packet' THEN 'Package'
            WHEN 'drop' THEN 'Drop'
            ELSE dose_unit
        END
        """
    )

    op.execute(
        """
        UPDATE histories
        SET dose_unit_snapshot = CASE dose_unit_snapshot
            WHEN 'mg' THEN 'Mg'
            WHEN 'ml' THEN 'Ml'
            WHEN 'tablet' THEN 'Tablet'
            WHEN 'capsule' THEN 'Capsule'
            WHEN 'packet' THEN 'Package'
            WHEN 'drop' THEN 'Drop'
            ELSE dose_unit_snapshot
        END
        """
    )
