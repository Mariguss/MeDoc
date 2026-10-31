"""added_manufacturer_to_medicines

Revision ID: a1c4e7f3b2d9
Revises: 2f2cc4b7af6f
Create Date: 2026-10-31 19:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1c4e7f3b2d9"
down_revision: str | Sequence[str] | None = "2f2cc4b7af6f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("medicines", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("manufacturer", sa.String(length=100), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("medicines", schema=None) as batch_op:
        batch_op.drop_column("manufacturer")
