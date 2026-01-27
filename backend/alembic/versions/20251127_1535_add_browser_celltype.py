"""add browser celltype

Revision ID: a1b2c3d4e5f6
Revises: 57a9a465710d
Create Date: 2025-11-27 15:35:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '57a9a465710d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 确保 celltype 枚举包含 browser
    # 使用 DO 块来安全地添加枚举值（如果不存在）
    op.execute("""
        DO $$ 
        BEGIN
            -- 检查并添加 'browser'
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'browser' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'celltype')
            ) THEN
                ALTER TYPE celltype ADD VALUE 'browser';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # 注意：PostgreSQL 不支持直接删除 ENUM 值
    # 如果需要完全回滚，需要重建整个 celltype 枚举
    pass

