"""add_student_type_and_exam_total_score

Revision ID: 12a5591c5111
Revises: 20260113_1400
Create Date: 2026-01-13 22:05:48.967712+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '12a5591c5111'
down_revision: Union[str, None] = '20260113_1400'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加学生类型字段和高中总分评价表"""

    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # ========================================
    # Step 1: 修改users表，添加student_type字段
    # ========================================
    print("Step 1: Adding student_type column to users table...")

    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]

        if 'student_type' not in columns:
            # 使用VARCHAR类型存储学生类型，兼容性更好
            op.add_column(
                'users',
                sa.Column(
                    'student_type',
                    sa.String(20),
                    nullable=True,
                    server_default='none',
                    comment='学生类型：none(未分科，含小学/初中/高中未分科阶段)/arts(文科)/science(理科)'
                )
            )
            print("  Added users.student_type")
        else:
            print("  users.student_type already exists")

    # ========================================
    # Step 2: 创建exam_total_scores表
    # ========================================
    print("Step 2: Creating exam_total_scores table...")

    if 'exam_total_scores' not in inspector.get_table_names():
        op.create_table(
            'exam_total_scores',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('exam_id', sa.Integer(), nullable=False, comment='考试ID'),
            sa.Column('student_id', sa.Integer(), nullable=False, comment='学生ID'),
            sa.Column('student_type', sa.String(20), nullable=False, comment='学生类型：none(未分科)/arts(文科)/science(理科)'),
            sa.Column('total_score', sa.Integer(), nullable=False, comment='考试总分（主要用于高考）'),
            sa.Column('c9_line', sa.Integer(), nullable=True, comment='C9线（顶尖大学）'),
            sa.Column('special_control_line', sa.Integer(), nullable=True, comment='特控线（特殊控制线/一本线）'),
            sa.Column('undergraduate_line', sa.Integer(), nullable=True, comment='本科线'),
            sa.Column('junior_college_line', sa.Integer(), nullable=True, comment='专科线'),
            sa.Column('reached_c9', sa.Boolean(), nullable=False, server_default='false', comment='是否达到C9线'),
            sa.Column('reached_special_control', sa.Boolean(), nullable=False, server_default='false', comment='是否达到特控线'),
            sa.Column('reached_undergraduate', sa.Boolean(), nullable=False, server_default='false', comment='是否达到本科线'),
            sa.Column('reached_junior_college', sa.Boolean(), nullable=False, server_default='false', comment='是否达到专科线'),
            sa.Column('is_absent', sa.Boolean(), nullable=False, server_default='false', comment='是否缺考'),
            sa.Column('is_cheated', sa.Boolean(), nullable=False, server_default='false', comment='是否作弊'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['student_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            comment='高中总分评价表'
        )
        op.create_index('ix_exam_total_scores_id', 'exam_total_scores', ['id'])
        op.create_index('idx_exam_total_scores', 'exam_total_scores', ['exam_id'])
        op.create_index('idx_student_total_scores', 'exam_total_scores', ['student_id'])
        op.create_index('idx_student_type', 'exam_total_scores', ['student_type'])
        op.create_unique_constraint('uq_exam_student_total', 'exam_total_scores', ['exam_id', 'student_id'])
        print("  Created table: exam_total_scores")
    else:
        print("  Table exam_total_scores already exists")

    print("\nMigration completed successfully!")


def downgrade() -> None:
    """回滚学生类型和高中总分评价表"""

    conn = op.get_bind()
    inspector = sa.inspect(conn)

    print("Rolling back changes...")

    # 删除exam_total_scores表
    if 'exam_total_scores' in inspector.get_table_names():
        op.drop_table('exam_total_scores')
        print("  Dropped table: exam_total_scores")

    # 删除users表的student_type字段
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]

        if 'student_type' in columns:
            op.drop_column('users', 'student_type')
            print("  Dropped users.student_type")

    print("\nRollback completed!")
