"""replace user email with username

Revision ID: 7c1ea46b925d
Revises: 2f727296f13f
Create Date: 2026-11-21 13:59:29.689434

"""

import sqlalchemy as sa
from alembic import op

revision = "7c1ea46b925d"
down_revision = "2f727296f13f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text('DELETE FROM "user"'))
    op.drop_column("user", "email")
    op.add_column("user", sa.Column("username", sa.String(), nullable=False))
    op.create_unique_constraint("user_username_key", "user", ["username"])


def downgrade() -> None:
    op.execute(sa.text('DELETE FROM "user"'))
    op.drop_column("user", "username")
    op.add_column("user", sa.Column("email", sa.String(), nullable=False))
    op.create_unique_constraint("user_email_key", "user", ["email"])
