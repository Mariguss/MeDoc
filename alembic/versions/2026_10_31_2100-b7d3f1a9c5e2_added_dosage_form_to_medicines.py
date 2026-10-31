"""added_dosage_form_to_medicines

Revision ID: b7d3f1a9c5e2
Revises: a1c4e7f3b2d9
Create Date: 2026-10-31 21:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7d3f1a9c5e2"
down_revision: str | Sequence[str] | None = "a1c4e7f3b2d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("medicines", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("dosage_form", sa.String(length=50), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("medicines", schema=None) as batch_op:
        batch_op.drop_column("dosage_form")
