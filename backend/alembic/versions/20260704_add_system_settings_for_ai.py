"""add system settings table for ai runtime config

Revision ID: 20260704_ai_settings
Revises: 20260704_self_study
Create Date: 2026-07-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260704_ai_settings"
down_revision: Union[str, None] = "20260704_self_study"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value_json", sa.JSON(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.UniqueConstraint("key", name="uq_system_settings_key"),
    )
    op.create_index("ix_system_settings_id", "system_settings", ["id"])
    op.create_index("ix_system_settings_key", "system_settings", ["key"])
    op.create_index("ix_system_settings_updated_by", "system_settings", ["updated_by"])


def downgrade() -> None:
    op.drop_index("ix_system_settings_updated_by", table_name="system_settings")
    op.drop_index("ix_system_settings_key", table_name="system_settings")
    op.drop_index("ix_system_settings_id", table_name="system_settings")
    op.drop_table("system_settings")
