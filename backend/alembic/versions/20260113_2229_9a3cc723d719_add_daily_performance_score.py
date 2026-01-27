"""add_daily_performance_score

Revision ID: 9a3cc723d719
Revises: 12a5591c5111
Create Date: 2026-01-13 22:29:48.365963+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '9a3cc723d719'
down_revision: Union[str, None] = '12a5591c5111'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加日常表现成绩表"""

    conn = op.get_bind()
    inspector = sa.inspect(conn)

    print("Creating daily_performance_scores table...")

    if 'daily_performance_scores' not in inspector.get_table_names():
        op.create_table(
            'daily_performance_scores',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('student_id', sa.Integer(), nullable=False, comment='学生ID'),
            sa.Column('classroom_id', sa.Integer(), nullable=False, comment='班级ID'),
            sa.Column('semester_id', sa.Integer(), nullable=True, comment='学期ID（可选）'),

            # 统计时间范围（灵活配置）
            sa.Column('period_name', sa.String(100), nullable=False, comment='统计周期名称'),
            sa.Column('start_date', sa.DateTime(), nullable=False, comment='统计开始日期'),
            sa.Column('end_date', sa.DateTime(), nullable=False, comment='统计结束日期'),

            # 原始数据统计
            sa.Column('positive_behavior_count', sa.Integer(), nullable=False, server_default='0', comment='正面行为次数'),
            sa.Column('positive_behavior_points', sa.Integer(), nullable=False, server_default='0', comment='正面行为总积分'),
            sa.Column('discipline_count', sa.Integer(), nullable=False, server_default='0', comment='违纪次数'),
            sa.Column('discipline_points', sa.Integer(), nullable=False, server_default='0', comment='违纪扣分'),
            sa.Column('attendance_present_count', sa.Integer(), nullable=False, server_default='0', comment='出勤次数'),
            sa.Column('attendance_late_count', sa.Integer(), nullable=False, server_default='0', comment='迟到次数'),
            sa.Column('attendance_leave_count', sa.Integer(), nullable=False, server_default='0', comment='请假次数'),
            sa.Column('attendance_absent_count', sa.Integer(), nullable=False, server_default='0', comment='缺勤次数'),
            sa.Column('duty_completed_count', sa.Integer(), nullable=False, server_default='0', comment='值日完成次数'),

            # 百分制成绩
            sa.Column('final_score', sa.Float(), nullable=False, comment='最终百分制成绩（0-100）'),
            sa.Column('grade_level', sa.String(20), nullable=True, comment='等级：优秀/良好/合格/不合格'),

            # 详细分类得分（JSON）
            sa.Column('detail_scores', sa.JSON(), nullable=True, comment='各分类详细得分和权重'),

            # 备注
            sa.Column('note', sa.Text(), nullable=True, comment='教师评语或备注'),

            # 元数据
            sa.Column('created_by', sa.Integer(), nullable=False, comment='创建人ID'),
            sa.Column('calculated_at', sa.DateTime(), nullable=False, comment='计算时间'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),

            sa.ForeignKeyConstraint(['student_id'], ['users.id']),
            sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id']),
            sa.ForeignKeyConstraint(['semester_id'], ['semesters.id']),
            sa.ForeignKeyConstraint(['created_by'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            comment='日常表现成绩表'
        )

        # 创建索引
        op.create_index('ix_daily_performance_scores_id', 'daily_performance_scores', ['id'])
        op.create_index('idx_daily_performance_student', 'daily_performance_scores', ['student_id'])
        op.create_index('idx_daily_performance_classroom', 'daily_performance_scores', ['classroom_id'])
        op.create_index('idx_daily_performance_period', 'daily_performance_scores', ['start_date', 'end_date'])
        op.create_index('idx_daily_performance_semester', 'daily_performance_scores', ['semester_id'])

        print("  Created table: daily_performance_scores")
    else:
        print("  Table daily_performance_scores already exists")

    print("\nMigration completed successfully!")


def downgrade() -> None:
    """回滚日常表现成绩表"""

    conn = op.get_bind()
    inspector = sa.inspect(conn)

    print("Rolling back daily_performance_scores...")

    if 'daily_performance_scores' in inspector.get_table_names():
        op.drop_table('daily_performance_scores')
        print("  Dropped table: daily_performance_scores")

    print("\nRollback completed!")
