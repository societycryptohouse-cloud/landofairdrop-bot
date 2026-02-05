"""add referral rewards table

Revision ID: 0003_add_referral_rewards
Revises: 0002_add_ref_code
Create Date: 2026-02-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_add_referral_rewards"
down_revision = "0002_add_ref_code"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "referral_rewards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("referrer_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("referred_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("referrer_user_id", "referred_user_id", name="uq_ref_reward"),
    )


def downgrade() -> None:
    op.drop_table("referral_rewards")
