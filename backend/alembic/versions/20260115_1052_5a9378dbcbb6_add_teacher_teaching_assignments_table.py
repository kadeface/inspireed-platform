"""add teacher teaching assignments table

Revision ID: 5a9378dbcbb6
Revises: 2e197c88672a
Create Date: 2026-01-15 10:52:20.274695+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5a9378dbcbb6'
down_revision = '2e197c88672a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建教师教学任务表
    op.create_table(
        'teacher_teaching_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False, comment='教师ID'),
        sa.Column('school_id', sa.Integer(), nullable=False, comment='学校ID'),
        sa.Column('grade_id', sa.Integer(), nullable=False, comment='年级ID'),
        sa.Column('classroom_id', sa.Integer(), nullable=False, comment='班级ID'),
        sa.Column('subject_id', sa.Integer(), nullable=False, comment='学科ID'),
        sa.Column('semester_id', sa.Integer(), nullable=False, comment='学期ID'),
        sa.Column('academic_year', sa.String(length=20), nullable=False, comment='学年，如 2023-2024'),
        sa.Column('assignment_type', sa.Enum('head_teacher', 'subject_teacher', name='teachingassignmenttype', native_enum=False), nullable=False, comment='任务类型：HEAD_TEACHER(班主任)/SUBJECT_TEACHER(学科教师)'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否激活'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id']),
        sa.ForeignKeyConstraint(['grade_id'], ['grades.id']),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id']),
        sa.ForeignKeyConstraint(['semester_id'], ['semesters.id']),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id']),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('teacher_id', 'semester_id', 'classroom_id', 'subject_id', name='uq_teacher_semester_classroom_subject')
    )
    
    # 创建索引
    op.create_index('idx_school_grade_subject', 'teacher_teaching_assignments', ['school_id', 'grade_id', 'subject_id'], unique=False)
    op.create_index('idx_semester_active', 'teacher_teaching_assignments', ['semester_id', 'is_active'], unique=False)
    op.create_index('idx_teacher_semester', 'teacher_teaching_assignments', ['teacher_id', 'semester_id'], unique=False)
    op.create_index(op.f('ix_teacher_teaching_assignments_academic_year'), 'teacher_teaching_assignments', ['academic_year'], unique=False)
    op.create_index(op.f('ix_teacher_teaching_assignments_classroom_id'), 'teacher_teaching_assignments', ['classroom_id'], unique=False)
    op.create_index(op.f('ix_teacher_teaching_assignments_grade_id'), 'teacher_teaching_assignments', ['grade_id'], unique=False)
    op.create_index(op.f('ix_teacher_teaching_assignments_id'), 'teacher_teaching_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_teacher_teaching_assignments_is_active'), 'teacher_teaching_assignments', ['is_active'], unique=False)
    op.create_index(op.f('ix_teacher_teaching_assignments_school_id'), 'teacher_teaching_assignments', ['school_id'], unique=False)
    op.create_index(op.f('ix_teacher_teaching_assignments_semester_id'), 'teacher_teaching_assignments', ['semester_id'], unique=False)
    op.create_index(op.f('ix_teacher_teaching_assignments_subject_id'), 'teacher_teaching_assignments', ['subject_id'], unique=False)
    op.create_index(op.f('ix_teacher_teaching_assignments_teacher_id'), 'teacher_teaching_assignments', ['teacher_id'], unique=False)


def downgrade() -> None:
    # 删除索引
    op.drop_index(op.f('ix_teacher_teaching_assignments_teacher_id'), table_name='teacher_teaching_assignments')
    op.drop_index(op.f('ix_teacher_teaching_assignments_subject_id'), table_name='teacher_teaching_assignments')
    op.drop_index(op.f('ix_teacher_teaching_assignments_semester_id'), table_name='teacher_teaching_assignments')
    op.drop_index(op.f('ix_teacher_teaching_assignments_school_id'), table_name='teacher_teaching_assignments')
    op.drop_index(op.f('ix_teacher_teaching_assignments_is_active'), table_name='teacher_teaching_assignments')
    op.drop_index(op.f('ix_teacher_teaching_assignments_id'), table_name='teacher_teaching_assignments')
    op.drop_index(op.f('ix_teacher_teaching_assignments_grade_id'), table_name='teacher_teaching_assignments')
    op.drop_index(op.f('ix_teacher_teaching_assignments_classroom_id'), table_name='teacher_teaching_assignments')
    op.drop_index(op.f('ix_teacher_teaching_assignments_academic_year'), table_name='teacher_teaching_assignments')
    op.drop_index('idx_teacher_semester', table_name='teacher_teaching_assignments')
    op.drop_index('idx_semester_active', table_name='teacher_teaching_assignments')
    op.drop_index('idx_school_grade_subject', table_name='teacher_teaching_assignments')
    
    # 删除表
    op.drop_table('teacher_teaching_assignments')
