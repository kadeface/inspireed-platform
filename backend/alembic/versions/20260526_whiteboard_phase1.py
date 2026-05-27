"""whiteboard phase1: groups, state, celltype

Revision ID: 20260526_whiteboard
Revises: 20260522_mathlab_contest
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260526_whiteboard"
down_revision: Union[str, None] = "20260522_mathlab_contest"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "session_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("group_index", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["class_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "group_index", name="uq_session_group_index"),
    )
    op.create_index("ix_session_groups_session_id", "session_groups", ["session_id"])

    op.create_table(
        "session_group_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("group_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["class_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "user_id", name="uq_session_group_member"),
    )
    op.create_index("ix_session_group_members_session_id", "session_group_members", ["session_id"])

    op.create_table(
        "whiteboard_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=False),
        sa.Column("document", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["class_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "cell_id", name="uq_whiteboard_session_cell"),
    )
    op.create_index("ix_whiteboard_states_session_id", "whiteboard_states", ["session_id"])

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum
                WHERE enumlabel = 'WHITEBOARD'
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'celltype')
            ) THEN
                ALTER TYPE celltype ADD VALUE 'WHITEBOARD';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.drop_table("whiteboard_states")
    op.drop_table("session_group_members")
    op.drop_table("session_groups")
