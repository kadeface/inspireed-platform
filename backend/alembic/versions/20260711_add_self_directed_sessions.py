"""add self directed learning sessions

Revision ID: 20260711_self_directed
Revises: 20260708_tutor_style
Create Date: 2026-07-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260711_self_directed"
down_revision: Union[str, None] = "20260708_tutor_style"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "self_directed_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("goal_text", sa.Text(), nullable=False),
        sa.Column("mission_why", sa.Text(), nullable=True),
        sa.Column("mission_success", sa.Text(), nullable=True),
        sa.Column("tutor_style", sa.String(length=50), nullable=False, server_default="default"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="generating"),
        sa.Column("prior_summary", sa.Text(), nullable=True),
        sa.Column("lesson_json", sa.JSON(), nullable=True),
        sa.Column("check_answers_json", sa.JSON(), nullable=True),
        sa.Column("vault_lesson_path", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_self_directed_sessions_student_id", "self_directed_sessions", ["student_id"])
    op.create_index("ix_self_directed_sessions_status", "self_directed_sessions", ["status"])
    op.create_index("ix_self_directed_sessions_created_at", "self_directed_sessions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_self_directed_sessions_created_at", table_name="self_directed_sessions")
    op.drop_index("ix_self_directed_sessions_status", table_name="self_directed_sessions")
    op.drop_index("ix_self_directed_sessions_student_id", table_name="self_directed_sessions")
    op.drop_table("self_directed_sessions")
