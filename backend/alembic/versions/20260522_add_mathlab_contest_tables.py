"""Add mathlab contest tables

Revision ID: 20260522_mathlab_contest
Revises: 20260405_guest_session
Create Date: 2026-05-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260522_mathlab_contest"
down_revision: Union[str, None] = "20260405_guest_session"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("mathlab_contests"):
        return

    op.create_table(
        "mathlab_contests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=True),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum("preparing", "running", "ended", name="mathlabconteststatus"),
            nullable=False,
            server_default="running",
        ),
        sa.Column("time_limit_sec", sa.Integer(), nullable=True),
        sa.Column("allow_resubmit", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("pass_threshold", sa.Integer(), nullable=False, server_default="85"),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["class_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cell_id"], ["cells.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mathlab_contests_session_id", "mathlab_contests", ["session_id"])
    op.create_index("ix_mathlab_contests_status", "mathlab_contests", ["status"])

    op.create_table(
        "mathlab_contest_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contest_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("auto_score", sa.Float(), nullable=False),
        sa.Column("auto_passed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("final_score", sa.Float(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("elapsed_sec", sa.Float(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contest_id"], ["mathlab_contests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("contest_id", "student_id", name="uq_mathlab_contest_student"),
    )
    op.create_index(
        "ix_mathlab_contest_submissions_contest_id",
        "mathlab_contest_submissions",
        ["contest_id"],
    )


def downgrade() -> None:
    op.drop_table("mathlab_contest_submissions")
    op.drop_table("mathlab_contests")
    op.execute("DROP TYPE IF EXISTS mathlabconteststatus")
