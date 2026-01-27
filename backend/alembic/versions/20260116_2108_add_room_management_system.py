"""add room management system

Revision ID: add_room_management_system
Revises:
Create Date: 2026-01-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2108roommanagementsystem'
down_revision = 'ac1989ccdaba'  # Latest migration: teacher_position_types
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='课室名称'),
        sa.Column('code', sa.String(length=50), nullable=True, comment='课室编码'),
        sa.Column('school_id', sa.Integer(), nullable=False, comment='所属学校ID'),
        sa.Column('building', sa.String(length=50), nullable=True, comment='楼栋'),
        sa.Column('floor', sa.Integer(), nullable=True, comment='楼层'),
        sa.Column('room_type', sa.String(length=50), nullable=False, comment='课室类型'),
        sa.Column('capacity', sa.Integer(), nullable=True, comment='座位容量'),
        sa.Column('equipment', sa.JSON(), nullable=True, comment='设备清单'),
        sa.Column('assigned_classroom_id', sa.Integer(), nullable=True, comment='固定分配的班级ID'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否激活'),
        sa.Column('description', sa.Text(), nullable=True, comment='课室描述'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id']),
        sa.ForeignKeyConstraint(['assigned_classroom_id'], ['classrooms.id']),
        comment='课室/物理教室表'
    )

    # Create indexes
    op.create_index('ix_rooms_code', 'rooms', ['code'], unique=True)
    op.create_index('ix_rooms_school_id', 'rooms', ['school_id'])
    op.create_index('idx_room_school_type', 'rooms', ['school_id', 'room_type'])

    # Add room_id column to class_sessions
    op.add_column(
        'class_sessions',
        sa.Column('room_id', sa.Integer(), nullable=True, comment='物理课室ID')
    )

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_class_sessions_room_id',
        'class_sessions', 'rooms',
        ['room_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create indexes for room_id
    op.create_index('ix_class_sessions_room_id', 'class_sessions', ['room_id'])
    op.create_index('idx_session_room_status', 'class_sessions', ['room_id', 'status'])


def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('idx_session_room_status', table_name='class_sessions')
    op.drop_index('ix_class_sessions_room_id', table_name='class_sessions')
    op.drop_index('idx_room_school_type', table_name='rooms')
    op.drop_index('ix_rooms_school_id', table_name='rooms')
    op.drop_index('ix_rooms_code', table_name='rooms')

    # Drop foreign key constraint
    op.drop_constraint('fk_class_sessions_room_id', 'class_sessions', type_='foreignkey')

    # Drop column from class_sessions
    op.drop_column('class_sessions', 'room_id')

    # Drop foreign key constraints
    op.drop_constraint('rooms_assigned_classroom_id_fkey', 'rooms', type_='foreignkey')
    op.drop_constraint('rooms_school_id_fkey', 'rooms', type_='foreignkey')

    # Drop table
    op.drop_table('rooms')
