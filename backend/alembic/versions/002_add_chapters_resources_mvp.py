"""Add chapters, resources and extend lessons for MVP

Revision ID: 002
Revises: 001
Create Date: 2025-10-17

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chapters and resources tables, extend lessons table"""

    # Create chapters table
    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chapters_id"), "chapters", ["id"], unique=False)
    op.create_index(op.f("ix_chapters_course_id"), "chapters", ["course_id"], unique=False)

    # Create resources table
    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chapter_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("resource_type", sa.String(length=20), nullable=False),
        # 文件相关
        sa.Column("file_url", sa.String(length=500), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        # 权限和状态
        sa.Column("is_official", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_downloadable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        # 统计
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("download_count", sa.Integer(), nullable=False, server_default="0"),
        # 创建者
        sa.Column("created_by", sa.Integer(), nullable=True),
        # 时间戳
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resources_id"), "resources", ["id"], unique=False)
    op.create_index(op.f("ix_resources_chapter_id"), "resources", ["chapter_id"], unique=False)
    op.create_index(
        op.f("ix_resources_resource_type"), "resources", ["resource_type"], unique=False
    )

    # Extend lessons table - add reference resource fields
    op.add_column("lessons", sa.Column("reference_resource_id", sa.Integer(), nullable=True))
    op.add_column("lessons", sa.Column("reference_notes", sa.Text(), nullable=True))
    op.add_column(
        "lessons", sa.Column("cell_count", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column("lessons", sa.Column("estimated_duration", sa.Integer(), nullable=True))
    op.add_column(
        "lessons", sa.Column("view_count", sa.Integer(), nullable=False, server_default="0")
    )

    op.create_index(
        op.f("ix_lessons_reference_resource_id"), "lessons", ["reference_resource_id"], unique=False
    )
    op.create_foreign_key(
        "fk_lessons_reference_resource_id",
        "lessons",
        "resources",
        ["reference_resource_id"],
        ["id"],
    )


def downgrade() -> None:
    """Remove chapters, resources tables and extended lesson fields"""

    # Remove extended fields from lessons
    op.drop_constraint("fk_lessons_reference_resource_id", "lessons", type_="foreignkey")
    op.drop_index(op.f("ix_lessons_reference_resource_id"), table_name="lessons")
    op.drop_column("lessons", "view_count")
    op.drop_column("lessons", "estimated_duration")
    op.drop_column("lessons", "cell_count")
    op.drop_column("lessons", "reference_notes")
    op.drop_column("lessons", "reference_resource_id")

    # Drop resources table
    op.drop_index(op.f("ix_resources_resource_type"), table_name="resources")
    op.drop_index(op.f("ix_resources_chapter_id"), table_name="resources")
    op.drop_index(op.f("ix_resources_id"), table_name="resources")
    op.drop_table("resources")

    # Drop chapters table
    op.drop_index(op.f("ix_chapters_course_id"), table_name="chapters")
    op.drop_index(op.f("ix_chapters_id"), table_name="chapters")
    op.drop_table("chapters")
