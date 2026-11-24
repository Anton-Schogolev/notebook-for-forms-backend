"""create tab content table

Revision ID: 0ce551a0ce8c
Revises: 9a71f3f99f44
Create Date: 2026-11-24 20:16:41.029113

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0ce551a0ce8c"
down_revision: str | Sequence[str] | None = "9a71f3f99f44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tabcontent",
        sa.Column("tab_id", sa.Uuid(), nullable=False),
        sa.Column("items", JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("tab_id"),
        sa.ForeignKeyConstraint(["tab_id"], ["tab.id"]),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tabcontent")
