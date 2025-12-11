"""add new subjects

Revision ID: f7e8d9c0b1a2
Revises: a1b2c3d4e5f6
Create Date: 2025-01-02 00:00:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7e8d9c0b1a2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new subjects: 科学, 心理, 音乐, 美术, 综合"""
    # 使用 INSERT ... ON CONFLICT DO NOTHING 来避免重复插入
    op.execute("""
        INSERT INTO subjects (name, code, description, display_order) VALUES
        ('科学', 'science', '科学学科', 11),
        ('心理', 'psychology', '心理学科', 12),
        ('音乐', 'music', '音乐学科', 13),
        ('美术', 'art', '美术学科', 14),
        ('综合', 'comprehensive', '综合学科', 15)
        ON CONFLICT (name) DO NOTHING;
    """)


def downgrade() -> None:
    """Remove new subjects"""
    op.execute("""
        DELETE FROM subjects 
        WHERE code IN ('science', 'psychology', 'music', 'art', 'comprehensive');
    """)
