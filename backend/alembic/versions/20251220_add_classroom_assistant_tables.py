"""Add classroom assistant tables

Revision ID: add_classroom_assistant_tables
Revises: add_library_asset_versions
Create Date: 2025-12-20 00:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "add_classroom_assistant_tables"
down_revision: Union[str, None] = "add_library_asset_versions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add classroom assistant tables and update Classroom model"""
    
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    columns = {}
    
    # Check existing columns for classrooms table
    if 'classrooms' in tables:
        columns['classrooms'] = [col['name'] for col in inspector.get_columns('classrooms')]
    
    # Update classrooms table
    if 'classrooms' in tables:
        if 'deputy_head_teacher_id' not in columns['classrooms']:
            op.add_column(
                'classrooms',
                sa.Column('deputy_head_teacher_id', sa.Integer(), nullable=True, comment='副班主任ID')
            )
            op.create_foreign_key(
                'fk_classrooms_deputy_head_teacher_id_users',
                'classrooms', 'users',
                ['deputy_head_teacher_id'], ['id']
            )
        
        if 'settings' not in columns['classrooms']:
            op.add_column(
                'classrooms',
                sa.Column('settings', sa.JSON(), nullable=True, comment='班级设置（JSON格式，如可见性控制等）')
            )
    
    # Create classroom_memberships table
    if 'classroom_memberships' not in tables:
        op.create_table(
            'classroom_memberships',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('classroom_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('role_in_class', sa.String(length=50), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
            sa.Column('is_primary_class', sa.Boolean(), nullable=False, server_default='0', comment='是否为主班级/默认进入班级'),
            sa.Column('student_no', sa.String(length=50), nullable=True, comment='学号/学籍号'),
            sa.Column('seat_no', sa.SmallInteger(), nullable=True, comment='座号'),
            sa.Column('cadre_title', sa.String(length=50), nullable=True, comment='班干部职务名称'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('classroom_id', 'user_id', name='uq_classroom_user'),
        )
        op.create_index(op.f('ix_classroom_memberships_classroom_id'), 'classroom_memberships', ['classroom_id'], unique=False)
        op.create_index(op.f('ix_classroom_memberships_user_id'), 'classroom_memberships', ['user_id'], unique=False)
        op.create_index(op.f('ix_classroom_memberships_role_in_class'), 'classroom_memberships', ['role_in_class'], unique=False)
        op.create_index(op.f('ix_classroom_memberships_is_active'), 'classroom_memberships', ['is_active'], unique=False)
        op.create_index('idx_membership_user_active', 'classroom_memberships', ['user_id', 'is_active'], unique=False)
        op.create_index('idx_membership_classroom_role', 'classroom_memberships', ['classroom_id', 'role_in_class'], unique=False)
    
    # Create attendance_sessions table
    if 'attendance_sessions' not in tables:
        op.create_table(
            'attendance_sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('classroom_id', sa.Integer(), nullable=False),
            sa.Column('initiated_by_user_id', sa.Integer(), nullable=False),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('window_seconds', sa.Integer(), nullable=False, server_default='60', comment='点名时间窗口（秒）'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
            sa.ForeignKeyConstraint(['initiated_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_attendance_sessions_classroom_id'), 'attendance_sessions', ['classroom_id'], unique=False)
        op.create_index(op.f('ix_attendance_sessions_initiated_by_user_id'), 'attendance_sessions', ['initiated_by_user_id'], unique=False)
    
    # Create attendance_entries table
    if 'attendance_entries' not in tables:
        op.create_table(
            'attendance_entries',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('session_id', sa.Integer(), nullable=False),
            sa.Column('student_id', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('updated_by_user_id', sa.Integer(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['session_id'], ['attendance_sessions.id'], ),
            sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('session_id', 'student_id', name='uq_attendance_session_student'),
        )
        op.create_index(op.f('ix_attendance_entries_session_id'), 'attendance_entries', ['session_id'], unique=False)
        op.create_index(op.f('ix_attendance_entries_student_id'), 'attendance_entries', ['student_id'], unique=False)
        op.create_index(op.f('ix_attendance_entries_updated_by_user_id'), 'attendance_entries', ['updated_by_user_id'], unique=False)
    
    # Create positive_behaviors table
    if 'positive_behaviors' not in tables:
        op.create_table(
            'positive_behaviors',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('classroom_id', sa.Integer(), nullable=False),
            sa.Column('student_id', sa.Integer(), nullable=False),
            sa.Column('behavior_type', sa.String(length=50), nullable=False),
            sa.Column('custom_behavior_text', sa.String(length=100), nullable=True, comment='自定义行为描述（仅当类型为other时）'),
            sa.Column('points', sa.SmallInteger(), nullable=False, comment='积分'),
            sa.Column('note', sa.String(length=100), nullable=True, comment='教师备注（0-50字）'),
            sa.Column('recorded_by_user_id', sa.Integer(), nullable=False),
            sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
            sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['recorded_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_positive_behaviors_classroom_id'), 'positive_behaviors', ['classroom_id'], unique=False)
        op.create_index(op.f('ix_positive_behaviors_student_id'), 'positive_behaviors', ['student_id'], unique=False)
        op.create_index(op.f('ix_positive_behaviors_recorded_by_user_id'), 'positive_behaviors', ['recorded_by_user_id'], unique=False)
        op.create_index(op.f('ix_positive_behaviors_recorded_at'), 'positive_behaviors', ['recorded_at'], unique=False)
        op.create_index('idx_positive_classroom_student_date', 'positive_behaviors', ['classroom_id', 'student_id', 'recorded_at'], unique=False)
        op.create_index('idx_positive_student_date', 'positive_behaviors', ['student_id', 'recorded_at'], unique=False)
    
    # Create discipline_records table
    if 'discipline_records' not in tables:
        op.create_table(
            'discipline_records',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('classroom_id', sa.Integer(), nullable=False),
            sa.Column('student_id', sa.Integer(), nullable=False),
            sa.Column('event_type', sa.String(length=50), nullable=False),
            sa.Column('custom_event_text', sa.String(length=100), nullable=True, comment='自定义事件描述（仅当类型为other时）'),
            sa.Column('note', sa.String(length=100), nullable=True, comment='教师备注（0-50字）'),
            sa.Column('recorded_by_user_id', sa.Integer(), nullable=False),
            sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
            sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['recorded_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_discipline_records_classroom_id'), 'discipline_records', ['classroom_id'], unique=False)
        op.create_index(op.f('ix_discipline_records_student_id'), 'discipline_records', ['student_id'], unique=False)
        op.create_index(op.f('ix_discipline_records_recorded_by_user_id'), 'discipline_records', ['recorded_by_user_id'], unique=False)
        op.create_index(op.f('ix_discipline_records_recorded_at'), 'discipline_records', ['recorded_at'], unique=False)
        op.create_index('idx_discipline_classroom_student_date', 'discipline_records', ['classroom_id', 'student_id', 'recorded_at'], unique=False)
        op.create_index('idx_discipline_student_date', 'discipline_records', ['student_id', 'recorded_at'], unique=False)
    
    # Create duty_rules table
    if 'duty_rules' not in tables:
        op.create_table(
            'duty_rules',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('classroom_id', sa.Integer(), nullable=False),
            sa.Column('rotation_type', sa.String(length=20), nullable=False),
            sa.Column('start_date', sa.DateTime(timezone=True), nullable=False, comment='轮换开始日期'),
            sa.Column('member_user_ids', sa.JSON(), nullable=False, comment='参与值日的学生ID列表（JSON数组）'),
            sa.Column('group_size', sa.SmallInteger(), nullable=False, server_default='1', comment='每组值日人数'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_duty_rules_classroom_id'), 'duty_rules', ['classroom_id'], unique=False)
    
    # Create duty_assignments table
    if 'duty_assignments' not in tables:
        op.create_table(
            'duty_assignments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('classroom_id', sa.Integer(), nullable=False),
            sa.Column('rule_id', sa.Integer(), nullable=True),
            sa.Column('duty_date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('assignee_user_id', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
            sa.Column('completed_by_user_id', sa.Integer(), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
            sa.ForeignKeyConstraint(['rule_id'], ['duty_rules.id'], ),
            sa.ForeignKeyConstraint(['assignee_user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['completed_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('classroom_id', 'duty_date', 'assignee_user_id', name='uq_classroom_date_assignee'),
        )
        op.create_index(op.f('ix_duty_assignments_classroom_id'), 'duty_assignments', ['classroom_id'], unique=False)
        op.create_index(op.f('ix_duty_assignments_rule_id'), 'duty_assignments', ['rule_id'], unique=False)
        op.create_index(op.f('ix_duty_assignments_duty_date'), 'duty_assignments', ['duty_date'], unique=False)
        op.create_index(op.f('ix_duty_assignments_assignee_user_id'), 'duty_assignments', ['assignee_user_id'], unique=False)
        op.create_index(op.f('ix_duty_assignments_completed_by_user_id'), 'duty_assignments', ['completed_by_user_id'], unique=False)
        op.create_index('idx_duty_classroom_date', 'duty_assignments', ['classroom_id', 'duty_date'], unique=False)


def downgrade() -> None:
    """Remove classroom assistant tables and revert Classroom changes"""
    
    # Drop tables in reverse order
    op.drop_table('duty_assignments')
    op.drop_table('duty_rules')
    op.drop_table('discipline_records')
    op.drop_table('positive_behaviors')
    op.drop_table('attendance_entries')
    op.drop_table('attendance_sessions')
    op.drop_table('classroom_memberships')
    
    # Revert classrooms table changes
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'classrooms' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('classrooms')]
        if 'settings' in columns:
            op.drop_column('classrooms', 'settings')
        if 'deputy_head_teacher_id' in columns:
            op.drop_constraint('fk_classrooms_deputy_head_teacher_id_users', 'classrooms', type_='foreignkey')
            op.drop_column('classrooms', 'deputy_head_teacher_id')
