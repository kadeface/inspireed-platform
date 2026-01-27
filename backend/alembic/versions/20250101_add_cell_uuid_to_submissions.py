"""add cell_uuid to activity_submissions

Revision ID: add_cell_uuid_to_submissions
Revises: 20251127_1535_add_browser_celltype
Create Date: 2025-01-01 00:00:00.000000

添加 cell_uuid 字段到 activity_submissions 表，用于直接存储 UUID，避免转换
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "add_cell_uuid_to_submissions"
down_revision = "a1b2c3d4e5f6"  # 20251127_1535_add_browser_celltype 的 revision ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 cell_uuid 字段到 activity_submissions 表
    op.add_column(
        "activity_submissions",
        sa.Column("cell_uuid", sa.String(length=36), nullable=True),
    )
    
    # 创建索引以提高查询性能
    op.create_index(
        op.f("ix_activity_submissions_cell_uuid"),
        "activity_submissions",
        ["cell_uuid"],
        unique=False,
    )


def downgrade() -> None:
    # 删除索引
    op.drop_index(
        op.f("ix_activity_submissions_cell_uuid"),
        table_name="activity_submissions",
    )
    
    # 删除字段
    op.drop_column("activity_submissions", "cell_uuid")

