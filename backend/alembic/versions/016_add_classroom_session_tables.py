"""add classroom session tables

Revision ID: 016_add_classroom_session
Revises: 015_fix_activity_submission
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '016_add_classroom_session'
down_revision = 'c9e2f8a1d5ef'  # 最新的迁移版本
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # 确保 classsessionstatus 枚举存在
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'classsessionstatus'
            ) THEN
                CREATE TYPE classsessionstatus AS ENUM ('pending', 'active', 'paused', 'ended');
            END IF;
        END $$;
    """)
    
    # 创建 class_sessions 表（如果不存在）
    if not inspector.has_table("class_sessions"):
        op.create_table(
            'class_sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('lesson_id', sa.Integer(), nullable=False),
            sa.Column('classroom_id', sa.Integer(), nullable=False),
            sa.Column('teacher_id', sa.Integer(), nullable=False),
            sa.Column('status', postgresql.ENUM('pending', 'active', 'paused', 'ended', name='classsessionstatus', create_type=False), nullable=False),
            sa.Column('scheduled_start', sa.DateTime(), nullable=True),
            sa.Column('actual_start', sa.DateTime(), nullable=True),
            sa.Column('ended_at', sa.DateTime(), nullable=True),
            sa.Column('duration_minutes', sa.Integer(), nullable=True),
            sa.Column('current_cell_id', sa.Integer(), nullable=True),
            sa.Column('current_activity_id', sa.Integer(), nullable=True),
            sa.Column('settings', sa.JSON(), nullable=True),
            sa.Column('total_students', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('active_students', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
            sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ),
            sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['current_cell_id'], ['cells.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_class_sessions_id'), 'class_sessions', ['id'], unique=False)
        op.create_index('ix_class_sessions_lesson_id', 'class_sessions', ['lesson_id'], unique=False)
        op.create_index('ix_class_sessions_classroom_id', 'class_sessions', ['classroom_id'], unique=False)
        op.create_index('ix_class_sessions_teacher_id', 'class_sessions', ['teacher_id'], unique=False)
        op.create_index('ix_class_sessions_status', 'class_sessions', ['status'], unique=False)
        op.create_index('ix_class_sessions_current_cell_id', 'class_sessions', ['current_cell_id'], unique=False)
        op.create_index('idx_session_status_teacher', 'class_sessions', ['teacher_id', 'status'], unique=False)
        op.create_index('idx_session_classroom_status', 'class_sessions', ['classroom_id', 'status'], unique=False)

    # 创建 student_session_participations 表（如果不存在）
    if not inspector.has_table("student_session_participations"):
        op.create_table(
            'student_session_participations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('session_id', sa.Integer(), nullable=False),
            sa.Column('student_id', sa.Integer(), nullable=False),
            sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('last_active_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('left_at', sa.DateTime(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('current_cell_id', sa.Integer(), nullable=True),
            sa.Column('completed_cells', sa.JSON(), nullable=True, server_default='[]'),
            sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
            sa.ForeignKeyConstraint(['session_id'], ['class_sessions.id'], ),
            sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('session_id', 'student_id', name='uq_session_student')
        )
        op.create_index(op.f('ix_student_session_participations_id'), 'student_session_participations', ['id'], unique=False)
        op.create_index('ix_student_session_participations_session_id', 'student_session_participations', ['session_id'], unique=False)
        op.create_index('ix_student_session_participations_student_id', 'student_session_participations', ['student_id'], unique=False)
        op.create_index('ix_student_session_participations_is_active', 'student_session_participations', ['is_active'], unique=False)
        op.create_index('ix_student_session_participations_current_cell_id', 'student_session_participations', ['current_cell_id'], unique=False)
        op.create_index('idx_participation_session_active', 'student_session_participations', ['session_id', 'is_active'], unique=False)

    # 在 activity_submissions 表中添加 session_id 字段（如果不存在）
    if inspector.has_table("activity_submissions"):
        columns = [col['name'] for col in inspector.get_columns('activity_submissions')]
        if 'session_id' not in columns:
            op.add_column('activity_submissions', sa.Column('session_id', sa.Integer(), nullable=True))
            # 创建外键约束（如果不存在）
            try:
                op.create_foreign_key(
                    'fk_activity_submission_session',
                    'activity_submissions',
                    'class_sessions',
                    ['session_id'],
                    ['id']
                )
            except Exception:
                pass  # 外键可能已存在
            
            # 创建索引（如果不存在）
            indexes = [idx['name'] for idx in inspector.get_indexes('activity_submissions')]
            if 'ix_activity_submissions_session_id' not in indexes:
                op.create_index('ix_activity_submissions_session_id', 'activity_submissions', ['session_id'], unique=False)


def downgrade() -> None:
    # 删除 activity_submissions 表的 session_id 字段
    op.drop_index('ix_activity_submissions_session_id', table_name='activity_submissions')
    op.drop_constraint('fk_activity_submission_session', 'activity_submissions', type_='foreignkey')
    op.drop_column('activity_submissions', 'session_id')

    # 删除 student_session_participations 表
    op.drop_index('idx_participation_session_active', table_name='student_session_participations')
    op.drop_index('ix_student_session_participations_current_cell_id', table_name='student_session_participations')
    op.drop_index('ix_student_session_participations_is_active', table_name='student_session_participations')
    op.drop_index('ix_student_session_participations_student_id', table_name='student_session_participations')
    op.drop_index('ix_student_session_participations_session_id', table_name='student_session_participations')
    op.drop_index(op.f('ix_student_session_participations_id'), table_name='student_session_participations')
    op.drop_table('student_session_participations')

    # 删除 class_sessions 表
    op.drop_index('idx_session_classroom_status', table_name='class_sessions')
    op.drop_index('idx_session_status_teacher', table_name='class_sessions')
    op.drop_index('ix_class_sessions_current_cell_id', table_name='class_sessions')
    op.drop_index('ix_class_sessions_status', table_name='class_sessions')
    op.drop_index('ix_class_sessions_teacher_id', table_name='class_sessions')
    op.drop_index('ix_class_sessions_classroom_id', table_name='class_sessions')
    op.drop_index('ix_class_sessions_lesson_id', table_name='class_sessions')
    op.drop_index(op.f('ix_class_sessions_id'), table_name='class_sessions')
    op.drop_table('class_sessions')
    op.execute("DROP TYPE IF EXISTS classsessionstatus")

