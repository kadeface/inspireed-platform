"""Add guest mode columns to class_sessions (align ORM with database)

Revision ID: 20260405_guest_session
Revises: 20260308_primary
Create Date: 2026-04-05

Without these columns, INSERT into class_sessions fails with UndefinedColumnError
and the API returns 500 Internal server error on "创建课堂".
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260405_guest_session"
down_revision: Union[str, None] = "20260308_primary"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("class_sessions"):
        return
    cols = {c["name"] for c in inspector.get_columns("class_sessions")}

    if "guest_access_enabled" not in cols:
        op.add_column(
            "class_sessions",
            sa.Column(
                "guest_access_enabled",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
    if "guest_access_code" not in cols:
        op.add_column(
            "class_sessions",
            sa.Column("guest_access_code", sa.String(length=8), nullable=True),
        )
    if "guest_count" not in cols:
        op.add_column(
            "class_sessions",
            sa.Column(
                "guest_count",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )

    # Unique guest codes (multiple NULLs allowed in PostgreSQL)
    inspector = sa.inspect(bind)
    indexes = {ix["name"] for ix in inspector.get_indexes("class_sessions")}
    if "ix_class_sessions_guest_access_code" not in indexes:
        op.create_index(
            "ix_class_sessions_guest_access_code",
            "class_sessions",
            ["guest_access_code"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("class_sessions"):
        return
    indexes = {ix["name"] for ix in inspector.get_indexes("class_sessions")}
    if "ix_class_sessions_guest_access_code" in indexes:
        op.drop_index("ix_class_sessions_guest_access_code", table_name="class_sessions")

    cols = {c["name"] for c in inspector.get_columns("class_sessions")}
    if "guest_count" in cols:
        op.drop_column("class_sessions", "guest_count")
    if "guest_access_code" in cols:
        op.drop_column("class_sessions", "guest_access_code")
    if "guest_access_enabled" in cols:
        op.drop_column("class_sessions", "guest_access_enabled")
