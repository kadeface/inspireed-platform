"""add tutor_style to self study sessions

Revision ID: 20260708_tutor_style
Revises: 20260704_ai_settings
Create Date: 2026-07-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_tutor_style"
down_revision: Union[str, None] = "20260704_ai_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "self_study_sessions",
        sa.Column("tutor_style", sa.String(length=50), nullable=False, server_default="default"),
    )


def downgrade() -> None:
    op.drop_column("self_study_sessions", "tutor_style")
