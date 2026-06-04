"""add site_statistics table for public visitor counter

Revision ID: 20260603_site_stats
Revises: 20260526_merge_heads
Create Date: 2026-06-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260603_site_stats"
down_revision: Union[str, None] = "20260526_merge_heads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "site_statistics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("total_visits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("today_visits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("today_date", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        """
        INSERT INTO site_statistics (id, total_visits, today_visits)
        VALUES (1, 0, 0)
        """
    )


def downgrade() -> None:
    op.drop_table("site_statistics")
