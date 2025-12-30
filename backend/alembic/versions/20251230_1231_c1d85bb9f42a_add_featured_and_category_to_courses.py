"""add_featured_and_category_to_courses

Revision ID: c1d85bb9f42a
Revises: 4eac54cf4de2
Create Date: 2025-12-30 12:31:43.336485+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1d85bb9f42a'
down_revision = '4eac54cf4de2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 is_featured 字段（是否精选）
    op.add_column('courses', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'))
    
    # 添加 category 字段（课程分类，如：人工智能、无人机、轮式机器人等）
    op.add_column('courses', sa.Column('category', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # 移除添加的字段
    op.drop_column('courses', 'category')
    op.drop_column('courses', 'is_featured')

