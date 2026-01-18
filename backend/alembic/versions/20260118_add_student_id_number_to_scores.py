"""Add student_id_number redundant field to scores table

Revision ID: add_student_id_number_scores
Revises: add_exam_level_v2
Create Date: 2026-01-18

This migration adds a student_id_number column to the scores table
as a redundant field to ensure permanent student-score associations,
independent of changes to the users.id primary key.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = 'add_student_id_number_scores'
down_revision = 'add_exam_level_v2'
branch_labels = None
depends_on = None


def upgrade():
    """添加student_id_number冗余字段"""

    # Step 1: 添加可空字段
    op.add_column(
        'scores',
        sa.Column(
            'student_id_number',
            sa.String(50),
            nullable=True,
            comment='学籍号/身份证号（冗余字段，用于永久关联）'
        )
    )

    # Step 2: 从users表复制学籍号数据
    op.execute("""
        UPDATE scores s
        SET student_id_number = (
            SELECT u.student_id_number
            FROM users u
            WHERE u.id = s.student_id
            AND u.student_id_number IS NOT NULL
            AND u.student_id_number <> ''
        )
    """)

    # Step 3: 验证数据完整性（检查是否有空值）
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT COUNT(*) FROM scores WHERE student_id_number IS NULL OR student_id_number = ''")
    ).scalar()

    if result > 0:
        raise Exception(
            f"发现 {result} 条成绩记录缺少学籍号，"
            f"请先确保users表中所有相关学生都有student_id_number"
        )

    # Step 4: 设置为NOT NULL
    op.alter_column(
        'scores',
        'student_id_number',
        nullable=False
    )

    # Step 5: 添加索引
    op.create_index(
        'idx_scores_student_id_number',
        'scores',
        ['student_id_number'],
        unique=False
    )

    op.create_index(
        'idx_scores_exam_student_number',
        'scores',
        ['exam_id', 'student_id_number']
    )

    op.create_index(
        'idx_scores_student_subject_number',
        'scores',
        ['student_id_number', 'subject_id']
    )

    # Step 6: 添加CHECK约束
    op.execute("""
        ALTER TABLE scores
        ADD CONSTRAINT chk_scores_student_id_number
        CHECK (student_id_number <> '')
    """)


def downgrade():
    """回滚：删除冗余字段"""

    # 删除约束
    op.execute("ALTER TABLE scores DROP CONSTRAINT IF EXISTS chk_scores_student_id_number")

    # 删除索引
    op.drop_index('idx_scores_student_subject_number', 'scores')
    op.drop_index('idx_scores_exam_student_number', 'scores')
    op.drop_index('idx_scores_student_id_number', 'scores')

    # 删除字段
    op.drop_column('scores', 'student_id_number')
