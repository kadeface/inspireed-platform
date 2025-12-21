"""Add version management to library_assets

Revision ID: add_library_asset_versions
Revises: add_view_count_library_assets
Create Date: 2025-12-19 00:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "add_library_asset_versions"
down_revision: Union[str, None] = "add_view_count_library_assets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add version management to library_assets"""
    
    # Check if version column already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('library_assets')]
    
    # Add version column to library_assets table (current version number)
    if 'version' not in columns:
        op.add_column(
            "library_assets",
            sa.Column(
                "version",
                sa.Integer(),
                nullable=False,
                server_default="1",
                comment="当前版本号",
            ),
        )
    
    # Check if table already exists
    tables = inspector.get_table_names()
    
    # Create library_asset_versions table to store historical versions
    if 'library_asset_versions' not in tables:
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
    
    # Initialize version for existing assets
    # Check if there are any existing version records (only if table already existed)
    table_was_new = 'library_asset_versions' not in tables
    if not table_was_new:
        # Table already existed, check if we need to initialize
        existing_versions = conn.execute(sa.text("SELECT COUNT(*) FROM library_asset_versions")).scalar()
        if existing_versions == 0:
            # Only insert if no versions exist yet
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
                AND id NOT IN (SELECT asset_id FROM library_asset_versions)
            """)
    else:
        # Table was just created, initialize versions
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
    """Remove version management from library_assets"""
    
    # Drop indexes
    op.drop_index("ix_library_asset_versions_asset_version", table_name="library_asset_versions")
    op.drop_index("ix_library_asset_versions_asset_id", table_name="library_asset_versions")
    
    # Drop table
    op.drop_table("library_asset_versions")
    
    # Remove version column
    op.drop_column("library_assets", "version")
