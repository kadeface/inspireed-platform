"""fix_celltype_enum_add_activity_flowchart

Revision ID: 2e224926b436
Revises: 016_add_classroom_session
Create Date: 2025-11-17 02:05:24.190147+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e224926b436'
down_revision = 'c9e2f8a1d5ef'  # 基于当前数据库版本
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 确保 celltype 枚举包含 activity 和 flowchart
    # 使用 DO 块来安全地添加枚举值（如果不存在）
    op.execute("""
        DO $$ 
        BEGIN
            -- 检查并添加 'activity'
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'activity' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'celltype')
            ) THEN
                ALTER TYPE celltype ADD VALUE 'activity';
            END IF;
            
            -- 检查并添加 'flowchart'
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'flowchart' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'celltype')
            ) THEN
                ALTER TYPE celltype ADD VALUE 'flowchart';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # 注意：PostgreSQL 不支持直接删除 ENUM 值
    # 如果需要完全回滚，需要重建整个 celltype 枚举
    pass

