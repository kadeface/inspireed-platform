"""Add view_count to library_assets

Revision ID: add_view_count_library_assets
Revises: add_knowledge_point_fields
Create Date: 2025-12-16 00:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_view_count_library_assets"
down_revision: Union[str, None] = "add_knowledge_point_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add view_count column to library_assets table"""

    # Add view_count column with server_default
    op.add_column(
        "library_assets",
        sa.Column(
            "view_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="点击/查看次数",
        ),
    )
    
    # Explicitly update any NULL values to 0 (safety measure)
    # This ensures all existing records have a proper value, even if server_default
    # doesn't immediately apply in some database configurations
    op.execute("UPDATE library_assets SET view_count = 0 WHERE view_count IS NULL")


def downgrade() -> None:
    """Remove view_count column from library_assets table"""

    # Drop column
    op.drop_column("library_assets", "view_count")
