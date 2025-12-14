"""Add grade_id to library_assets

Revision ID: add_grade_id_library_assets
Revises: 97119fda8aae
Create Date: 2025-12-14 08:26:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_grade_id_library_assets"
down_revision: Union[str, None] = "97119fda8aae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add grade_id column to library_assets table"""

    # Add grade_id column to library_assets
    op.add_column(
        "library_assets",
        sa.Column(
            "grade_id",
            sa.Integer(),
            nullable=True,
            comment="年级ID（可选，NULL表示跨年级通用）",
        ),
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        "fk_library_assets_grade_id",
        "library_assets",
        "grades",
        ["grade_id"],
        ["id"],
        ondelete="SET NULL",
    )
    
    # Create index for grade_id (combined with school_id for performance)
    op.create_index(
        "ix_library_assets_school_grade",
        "library_assets",
        ["school_id", "grade_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove grade_id column from library_assets table"""

    # Drop index
    op.drop_index("ix_library_assets_school_grade", table_name="library_assets")
    
    # Drop foreign key constraint
    op.drop_constraint("fk_library_assets_grade_id", "library_assets", type_="foreignkey")
    
    # Drop column
    op.drop_column("library_assets", "grade_id")
