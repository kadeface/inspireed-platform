"""Add library_assets table and resource.asset_id

Revision ID: 017
Revises: 016
Create Date: 2025-12-12

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "017"
down_revision: Union[str, None] = "016_add_classroom_session"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create library_assets table and add asset_id to resources"""

    # Create library_assets table
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
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for library_assets
    op.create_index(
        op.f("ix_library_assets_id"), "library_assets", ["id"], unique=False
    )
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

    # Add asset_id column to resources table
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


def downgrade() -> None:
    """Remove library_assets table and asset_id from resources"""

    # Remove asset_id from resources
    op.drop_index(op.f("ix_resources_asset_id"), table_name="resources")
    op.drop_constraint("fk_resources_asset_id", "resources", type_="foreignkey")
    op.drop_column("resources", "asset_id")

    # Drop library_assets table
    op.drop_index("ix_library_assets_sha256", table_name="library_assets")
    op.drop_index(
        "ix_library_assets_school_visibility_status", table_name="library_assets"
    )
    op.drop_index("ix_library_assets_school_type", table_name="library_assets")
    op.drop_index("ix_library_assets_school_updated", table_name="library_assets")
    op.drop_index(op.f("ix_library_assets_id"), table_name="library_assets")
    op.drop_table("library_assets")
