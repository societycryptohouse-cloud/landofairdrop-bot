"""add ref_code to users

Revision ID: 0002_add_ref_code
Revises: 0001_initial
Create Date: 2026-02-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_ref_code"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("ref_code", sa.String(length=16), nullable=True))
    op.create_unique_constraint("uq_users_ref_code", "users", ["ref_code"])


def downgrade() -> None:
    op.drop_constraint("uq_users_ref_code", "users", type_="unique")
    op.drop_column("users", "ref_code")
