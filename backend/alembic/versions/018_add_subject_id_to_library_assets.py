"""Add subject_id to library_assets

Revision ID: 018
Revises: 017
Create Date: 2025-01-15

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "018"
down_revision: Union[str, None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add subject_id column to library_assets table"""

    # Add subject_id column to library_assets
    op.add_column(
        "library_assets",
        sa.Column(
            "subject_id",
            sa.Integer(),
            nullable=True,
            comment="学科ID（可选）",
        ),
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        "fk_library_assets_subject_id",
        "library_assets",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="SET NULL",
    )
    
    # Create index for subject_id
    op.create_index(
        "ix_library_assets_school_subject",
        "library_assets",
        ["school_id", "subject_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove subject_id column from library_assets table"""

    # Drop index
    op.drop_index("ix_library_assets_school_subject", table_name="library_assets")
    
    # Drop foreign key constraint
    op.drop_constraint("fk_library_assets_subject_id", "library_assets", type_="foreignkey")
    
    # Drop column
    op.drop_column("library_assets", "subject_id")

