"""add uppercase activity flowchart browser to celltype enum

Revision ID: be0419b1a426
Revises: e8232dde319d
Create Date: 2025-12-05 02:36:05.048528+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be0419b1a426'
down_revision = 'e8232dde319d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加大写的枚举值以匹配代码中的使用
    # 代码使用 ACTIVITY, FLOWCHART, BROWSER，但数据库中只有小写版本
    op.execute("""
        DO $$ 
        BEGIN
            -- 检查并添加 'ACTIVITY'（大写）
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'ACTIVITY' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'celltype')
            ) THEN
                ALTER TYPE celltype ADD VALUE 'ACTIVITY';
            END IF;
            
            -- 检查并添加 'FLOWCHART'（大写）
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'FLOWCHART' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'celltype')
            ) THEN
                ALTER TYPE celltype ADD VALUE 'FLOWCHART';
            END IF;
            
            -- 检查并添加 'BROWSER'（大写）
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'BROWSER' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'celltype')
            ) THEN
                ALTER TYPE celltype ADD VALUE 'BROWSER';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # 注意：PostgreSQL 不支持直接删除 ENUM 值
    # 如果需要完全回滚，需要重建整个 celltype 枚举
    pass

