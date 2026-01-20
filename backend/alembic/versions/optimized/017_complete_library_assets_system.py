"""Complete library assets system

This migration consolidates 6 separate library_assets migrations into a single,
well-structured migration that creates the complete library_assets table with all
fields, indexes, and the version management system.

Replaces:
- 017_add_library_assets_and_resource_asset_id.py
- 018_add_subject_id_to_library_assets.py
- 20251214_0826_add_grade_id_to_library_assets.py
- 20251215_add_knowledge_point_fields_to_library_assets.py
- 20251216_add_view_count_to_library_assets.py
- 20251219_add_library_asset_versions.py

Revision ID: 017_complete_library_assets
Revises: 016_add_classroom_session
Create Date: 2026-01-18

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "017_complete_library_assets"
down_revision: Union[str, None] = "016_add_classroom_session"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create complete library_assets system with all fields and version management"""

    conn = op.get_bind()
    inspector = inspect(conn)

    # ========================================================================
    # PART 1: Create library_assets table (if not exists)
    # ========================================================================
    if 'library_assets' not in inspector.get_table_names():
        op.create_table(
            "library_assets",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("school_id", sa.Integer(), nullable=False, comment="所属学校ID"),
            sa.Column("owner_user_id", sa.Integer(), nullable=False, comment="上传者ID"),
            sa.Column("title", sa.String(length=200), nullable=False, comment="资源标题"),
            sa.Column("description", sa.Text(), nullable=True, comment="资源描述"),
            sa.Column(
                "asset_type",
                sa.String(length=20),
                nullable=False,
                comment="资源类型：pdf/video/image/audio/document/link/zip/other",
            ),
            sa.Column("subject_id", sa.Integer(), nullable=True, comment="学科ID（可选）"),
            sa.Column("grade_id", sa.Integer(), nullable=True, comment="年级ID（可选，NULL表示跨年级通用）"),
            sa.Column(
                "knowledge_point_category",
                sa.String(length=100),
                nullable=True,
                comment="知识点分类（如：计算类/速算技巧、几何类/图形认知）",
            ),
            sa.Column(
                "knowledge_point_name",
                sa.String(length=200),
                nullable=True,
                comment="具体知识点名称（如：乘法口诀可视化）",
            ),
            sa.Column("mime_type", sa.String(length=100), nullable=True, comment="MIME类型"),
            sa.Column("size_bytes", sa.Integer(), nullable=True, comment="文件大小（字节）"),
            sa.Column(
                "storage_provider",
                sa.String(length=20),
                nullable=False,
                server_default="local",
                comment="存储提供商：local/minio",
            ),
            sa.Column(
                "storage_key", sa.String(length=500), nullable=False, comment="存储键/相对路径"
            ),
            sa.Column(
                "public_url",
                sa.String(length=500),
                nullable=True,
                comment="公开访问URL（如 /uploads/resources/xxx）",
            ),
            sa.Column(
                "sha256", sa.String(length=64), nullable=True, comment="文件SHA256哈希（用于去重）"
            ),
            sa.Column("thumbnail_url", sa.String(length=500), nullable=True, comment="缩略图URL"),
            sa.Column("page_count", sa.Integer(), nullable=True, comment="页数（PDF）"),
            sa.Column(
                "duration_seconds", sa.Integer(), nullable=True, comment="时长（视频/音频，秒）"
            ),
            sa.Column(
                "visibility",
                sa.String(length=20),
                nullable=False,
                server_default="teacher_only",
                comment="可见性：teacher_only（仅上传者）/school（全校可见）",
            ),
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default="active",
                comment="状态：active/processing/disabled/deleted",
            ),
            sa.Column(
                "view_count",
                sa.Integer(),
                nullable=False,
                server_default="0",
                comment="点击/查看次数",
            ),
            sa.Column(
                "version",
                sa.Integer(),
                nullable=False,
                server_default="1",
                comment="当前版本号",
            ),
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
            sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["grade_id"], ["grades.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )

        # Create indexes for library_assets
        op.create_index(op.f("ix_library_assets_id"), "library_assets", ["id"], unique=False)
        op.create_index(
            "ix_library_assets_school_updated",
            "library_assets",
            ["school_id", "updated_at"],
            unique=False,
        )
        op.create_index(
            "ix_library_assets_school_type",
            "library_assets",
            ["school_id", "asset_type"],
            unique=False,
        )
        op.create_index(
            "ix_library_assets_school_visibility_status",
            "library_assets",
            ["school_id", "visibility", "status"],
            unique=False,
        )
        op.create_index(
            "ix_library_assets_sha256", "library_assets", ["sha256"], unique=False
        )
        op.create_index(
            "ix_library_assets_school_subject",
            "library_assets",
            ["school_id", "subject_id"],
            unique=False,
        )
        op.create_index(
            "ix_library_assets_school_grade",
            "library_assets",
            ["school_id", "grade_id"],
            unique=False,
        )
        op.create_index(
            "ix_library_assets_knowledge_point",
            "library_assets",
            ["school_id", "subject_id", "knowledge_point_category"],
            unique=False,
        )

    # ========================================================================
    # PART 2: Add asset_id to resources table
    # ========================================================================
    columns = [col['name'] for col in inspector.get_columns('resources')]
    if 'asset_id' not in columns:
        op.add_column(
            "resources",
            sa.Column(
                "asset_id",
                sa.Integer(),
                nullable=True,
                comment="引用的资源库资产ID",
            ),
        )
        op.create_foreign_key(
            "fk_resources_asset_id",
            "resources",
            "library_assets",
            ["asset_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index(
            op.f("ix_resources_asset_id"), "resources", ["asset_id"], unique=False
        )

    # ========================================================================
    # PART 3: Create library_asset_versions table
    # ========================================================================
    if 'library_asset_versions' not in inspector.get_table_names():
        op.create_table(
            "library_asset_versions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column(
                "asset_id",
                sa.Integer(),
                nullable=False,
                comment="资源库资产ID",
            ),
            sa.Column(
                "version",
                sa.Integer(),
                nullable=False,
                comment="版本号",
            ),
            sa.Column(
                "storage_key",
                sa.String(length=500),
                nullable=False,
                comment="存储键/相对路径",
            ),
            sa.Column(
                "public_url",
                sa.String(length=500),
                nullable=True,
                comment="公开访问URL",
            ),
            sa.Column(
                "size_bytes",
                sa.Integer(),
                nullable=True,
                comment="文件大小（字节）",
            ),
            sa.Column(
                "sha256",
                sa.String(length=64),
                nullable=True,
                comment="文件SHA256哈希",
            ),
            sa.Column(
                "created_by",
                sa.Integer(),
                nullable=False,
                comment="创建此版本的用户ID",
            ),
            sa.Column(
                "change_note",
                sa.Text(),
                nullable=True,
                comment="版本变更说明",
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                comment="创建时间",
            ),
            sa.ForeignKeyConstraint(
                ["asset_id"],
                ["library_assets.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["created_by"],
                ["users.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("asset_id", "version", name="uq_asset_version"),
        )

        # Create indexes for performance
        op.create_index(
            "ix_library_asset_versions_asset_id",
            "library_asset_versions",
            ["asset_id"],
        )
        op.create_index(
            "ix_library_asset_versions_asset_version",
            "library_asset_versions",
            ["asset_id", "version"],
        )

        # Initialize versions for existing assets
        op.execute("""
            INSERT INTO library_asset_versions (asset_id, version, storage_key, public_url, size_bytes, sha256, created_by, created_at)
            SELECT
                id as asset_id,
                COALESCE(version, 1) as version,
                storage_key,
                public_url,
                size_bytes,
                sha256,
                owner_user_id as created_by,
                created_at
            FROM library_assets
            WHERE status = 'active'
        """)


def downgrade() -> None:
    """Remove complete library_assets system"""

    # Part 3: Drop library_asset_versions table
    op.drop_index("ix_library_asset_versions_asset_version", table_name="library_asset_versions")
    op.drop_index("ix_library_asset_versions_asset_id", table_name="library_asset_versions")
    op.drop_table("library_asset_versions")

    # Part 2: Remove asset_id from resources
    op.drop_index(op.f("ix_resources_asset_id"), table_name="resources")
    op.drop_constraint("fk_resources_asset_id", "resources", type_="foreignkey")
    op.drop_column("resources", "asset_id")

    # Part 1: Drop library_assets table
    op.drop_index("ix_library_assets_knowledge_point", table_name="library_assets")
    op.drop_index("ix_library_assets_school_grade", table_name="library_assets")
    op.drop_index("ix_library_assets_school_subject", table_name="library_assets")
    op.drop_index("ix_library_assets_sha256", table_name="library_assets")
    op.drop_index("ix_library_assets_school_visibility_status", table_name="library_assets")
    op.drop_index("ix_library_assets_school_type", table_name="library_assets")
    op.drop_index("ix_library_assets_school_updated", table_name="library_assets")
    op.drop_index(op.f("ix_library_assets_id"), table_name="library_assets")
    op.drop_table("library_assets")
