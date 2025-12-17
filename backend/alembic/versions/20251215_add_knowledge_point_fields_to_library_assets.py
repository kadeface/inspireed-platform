"""Add knowledge_point_category and knowledge_point_name to library_assets

Revision ID: add_knowledge_point_fields
Revises: add_grade_id_library_assets
Create Date: 2025-12-15 00:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_knowledge_point_fields"
down_revision: Union[str, None] = "add_grade_id_library_assets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add knowledge_point_category and knowledge_point_name columns to library_assets table"""

    # Add knowledge_point_category column
    op.add_column(
        "library_assets",
        sa.Column(
            "knowledge_point_category",
            sa.String(length=100),
            nullable=True,
            comment="知识点分类（如：计算类/速算技巧、几何类/图形认知）",
        ),
    )
    
    # Add knowledge_point_name column
    op.add_column(
        "library_assets",
        sa.Column(
            "knowledge_point_name",
            sa.String(length=200),
            nullable=True,
            comment="具体知识点名称（如：乘法口诀可视化）",
        ),
    )
    
    # Create index for knowledge_point_category (combined with school_id and subject_id for performance)
    op.create_index(
        "ix_library_assets_knowledge_point",
        "library_assets",
        ["school_id", "subject_id", "knowledge_point_category"],
        unique=False,
    )


def downgrade() -> None:
    """Remove knowledge_point_category and knowledge_point_name columns from library_assets table"""

    # Drop index
    op.drop_index("ix_library_assets_knowledge_point", table_name="library_assets")
    
    # Drop columns
    op.drop_column("library_assets", "knowledge_point_name")
    op.drop_column("library_assets", "knowledge_point_category")
