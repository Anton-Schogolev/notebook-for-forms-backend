"""cascade tab content deletion

Revision ID: 9372eaa22dfc
Revises: 0ce551a0ce8c
Create Date: 2026-11-24 21:52:46.019626

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9372eaa22dfc"
down_revision: str | Sequence[str] | None = "0ce551a0ce8c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("tabcontent_tab_id_fkey", "tabcontent", type_="foreignkey")
    op.create_foreign_key(
        "tabcontent_tab_id_fkey",
        "tabcontent",
        "tab",
        ["tab_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("tabcontent_tab_id_fkey", "tabcontent", type_="foreignkey")
    op.create_foreign_key(
        "tabcontent_tab_id_fkey",
        "tabcontent",
        "tab",
        ["tab_id"],
        ["id"],
    )
