"""add exam room arrangement system

Revision ID: 37524cdfebdb
Revises: 2108roommanagementsystem
Create Date: 2026-01-17 09:59:22.703962+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37524cdfebdb'
down_revision = '2108roommanagementsystem'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create exam_rooms table
    op.create_table(
        'exam_rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False, comment='考试ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='考场名称：第1考场'),
        sa.Column('school_id', sa.Integer(), nullable=False, comment='学校ID'),
        sa.Column('room_id', sa.Integer(), nullable=True, comment='使用的教室ID'),
        sa.Column('capacity', sa.Integer(), nullable=False, server_default='30', comment='考场容量'),
        sa.Column('seat_count', sa.Integer(), nullable=False, server_default='0', comment='实际座位数'),
        sa.Column('exam_number_start', sa.String(length=20), nullable=True, comment='起始考号'),
        sa.Column('exam_number_end', sa.String(length=20), nullable=True, comment='结束考号'),
        sa.Column('arrangement_type', sa.String(length=20), nullable=False, server_default='by_class', comment='编排类型：by_class/mixed'),
        sa.Column('seat_pattern', sa.String(length=20), nullable=False, server_default='s_shape', comment='座位排列：sequential/s_shape'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id']),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id']),
        sa.Index('ix_exam_rooms_id', 'id'),
        sa.Index('idx_exam_rooms_exam_id', 'exam_id'),
        comment='考场表'
    )

    # Create exam_room_students table
    op.create_table(
        'exam_room_students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False, comment='考场ID'),
        sa.Column('student_id', sa.Integer(), nullable=False, comment='学生ID'),
        sa.Column('exam_number', sa.String(length=20), nullable=False, comment='考号'),
        sa.Column('seat_number', sa.Integer(), nullable=False, comment='座位号 1-30'),
        sa.Column('table_number', sa.Integer(), nullable=True, comment='桌子号（可选）'),
        sa.Column('student_id_number', sa.String(length=50), nullable=True, comment='学籍号'),
        sa.Column('student_name', sa.String(length=100), nullable=True, comment='学生姓名（快照）'),
        sa.Column('school_id', sa.Integer(), nullable=True, comment='学校ID'),
        sa.Column('classroom_id', sa.Integer(), nullable=True, comment='班级ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['room_id'], ['exam_rooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id']),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id']),
        sa.Index('ix_exam_room_students_id', 'id'),
        sa.Index('idx_exam_room_students_room_id', 'room_id'),
        sa.UniqueConstraint('room_id', 'exam_number', name='uq_room_exam_number'),
        sa.UniqueConstraint('room_id', 'seat_number', name='uq_room_seat_number'),
        comment='考场学生关联表'
    )

    # Create exam_proctors table
    op.create_table(
        'exam_proctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False, comment='考场ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='教师用户ID'),
        sa.Column('proctor_type', sa.String(length=20), nullable=False, comment='监考类型：primary/assistant'),
        sa.Column('responsibilities', sa.JSON(), nullable=True, comment='职责列表'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['room_id'], ['exam_rooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.Index('ix_exam_proctors_id', 'id'),
        sa.Index('idx_exam_proctors_room_id', 'room_id'),
        comment='监考教师表'
    )


def downgrade() -> None:
    op.drop_table('exam_proctors')
    op.drop_table('exam_room_students')
    op.drop_table('exam_rooms')

