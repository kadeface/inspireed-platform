"""add interactive collect submissions

Revision ID: 20261011_collect
Revises: 20260711_self_directed
Create Date: 2026-10-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261011_collect"
down_revision: Union[str, None] = "20260711_self_directed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interactive_collect_submissions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("collect_key", sa.String(length=64), nullable=False),
        sa.Column("student_label", sa.String(length=100), nullable=False, server_default="未署名"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "ix_interactive_collect_submissions_collect_key",
        "interactive_collect_submissions",
        ["collect_key"],
    )
    op.create_index(
        "ix_interactive_collect_submissions_created_at",
        "interactive_collect_submissions",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_interactive_collect_submissions_created_at",
        table_name="interactive_collect_submissions",
    )
    op.drop_index(
        "ix_interactive_collect_submissions_collect_key",
        table_name="interactive_collect_submissions",
    )
    op.drop_table("interactive_collect_submissions")
