"""add exam_level field to exams table

Revision ID: add_exam_level_v2
Revises: 37524cdfebdb
Create Date: 2026-01-18 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_exam_level_v2'
down_revision = '37524cdfebdb'
branch_labels = None
depends_on = None


def upgrade():
    """添加 exam_level 字段到 exams 表"""

    # 添加 exam_level 字段为 VARCHAR，默认值为 'school'
    op.add_column(
        'exams',
        sa.Column(
            'exam_level',
            sa.String(20),
            nullable=False,
            server_default='school',
            comment='考试级别：school/district/city'
        )
    )

    # 更新现有数据：根据 exam_type 设置 exam_level
    op.execute("""
        UPDATE exams
        SET exam_level = CASE
            WHEN exam_type = 'district_unified' THEN 'district'
            ELSE 'school'
        END
    """)

    # 添加 CHECK 约束确保值有效
    op.execute("""
        ALTER TABLE exams
        ADD CONSTRAINT chk_exam_level
        CHECK (exam_level IN ('school', 'district', 'city'))
    """)


def downgrade():
    """移除 exam_level 字段"""

    # 删除约束
    op.execute("ALTER TABLE exams DROP CONSTRAINT IF EXISTS chk_exam_level")

    # 删除 exam_level 字段
    op.drop_column('exams', 'exam_level')
