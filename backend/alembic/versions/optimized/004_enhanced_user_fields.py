"""Enhanced user fields

This migration consolidates user-related field additions from multiple migrations:
- Adds last_login field
- Adds student_id_number field
- Extends users table with classroom relationships

Replaces:
- 20251108_1358_088e21d1e159_add_classrooms_and_user_scope_fields.py (partial)
- 20251221_add_last_login_to_users.py
- 20251221_1723_add_student_id_number_to_users.py

Revision ID: 004_enhanced_user_fields
Revises: 003_add_organization_tables
Create Date: 2026-01-18

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "004_enhanced_user_fields"
down_revision: Union[str, None] = "003_add_organization_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add enhanced fields to users table"""

    conn = op.get_bind()
    inspector = inspect(conn)
    user_columns = [col['name'] for col in inspector.get_columns('users')]

    # ========================================================================
    # PART 1: Add classroom relationship fields
    # ========================================================================
    if 'region_id' not in user_columns:
        op.add_column(
            'users',
            sa.Column('region_id', sa.Integer(), nullable=True, comment='所属区域ID')
        )
        op.create_foreign_key(
            'fk_users_region_id',
            'users', 'regions',
            ['region_id'], ['id'],
            ondelete='SET NULL'
        )
        op.create_index('ix_users_region_id', 'users', ['region_id'])

    if 'grade_id' not in user_columns:
        op.add_column(
            'users',
            sa.Column('grade_id', sa.Integer(), nullable=True, comment='所属年级ID')
        )
        op.create_foreign_key(
            'fk_users_grade_id',
            'users', 'grades',
            ['grade_id'], ['id'],
            ondelete='SET NULL'
        )
        op.create_index('ix_users_grade_id', 'users', ['grade_id'])

    if 'classroom_id' not in user_columns:
        op.add_column(
            'users',
            sa.Column('classroom_id', sa.Integer(), nullable=True, comment='所属班级ID')
        )
        op.create_foreign_key(
            'fk_users_classroom_id',
            'users', 'classrooms',
            ['classroom_id'], ['id'],
            ondelete='SET NULL'
        )
        op.create_index('ix_users_classroom_id', 'users', ['classroom_id'])

    # ========================================================================
    # PART 2: Add last_login field
    # ========================================================================
    if 'last_login' not in user_columns:
        op.add_column(
            'users',
            sa.Column(
                'last_login',
                sa.DateTime(timezone=True),
                nullable=True,
                comment='最后登录时间'
            )
        )
        op.create_index('ix_users_last_login', 'users', ['last_login'])

    # ========================================================================
    # PART 3: Add student_id_number field
    # ========================================================================
    if 'student_id_number' not in user_columns:
        op.add_column(
            'users',
            sa.Column(
                'student_id_number',
                sa.String(length=50),
                nullable=True,
                comment='学生学号（唯一索引）',
            )
        )
        # Create unique index for student_id_number
        op.create_index(
            'ix_users_student_id_number',
            'users',
            ['student_id_number'],
            unique=True
        )

    # ========================================================================
    # PART 4: Add composite index for common queries
    # ========================================================================
    # Check if index already exists before creating
    indexes = inspector.get_indexes('users')
    index_names = [idx['name'] for idx in indexes]

    if 'ix_users_school_classroom' not in index_names:
        op.create_index(
            'ix_users_school_classroom',
            'users',
            ['school_id', 'classroom_id']
        )

    if 'ix_users_school_role' not in index_names:
        op.create_index(
            'ix_users_school_role',
            'users',
            ['school_id', 'role']
        )


def downgrade() -> None:
    """Remove enhanced fields from users table"""

    conn = op.get_bind()
    inspector = inspect(conn)
    indexes = inspector.get_indexes('users')

    # Part 4: Drop composite indexes
    index_names = [idx['name'] for idx in indexes]
    if 'ix_users_school_role' in index_names:
        op.drop_index('ix_users_school_role', table_name='users')
    if 'ix_users_school_classroom' in index_names:
        op.drop_index('ix_users_school_classroom', table_name='users')

    # Part 3: Drop student_id_number
    op.drop_index('ix_users_student_id_number', table_name='users')
    op.drop_column('users', 'student_id_number')

    # Part 2: Drop last_login
    op.drop_index('ix_users_last_login', table_name='users')
    op.drop_column('users', 'last_login')

    # Part 1: Drop classroom relationship fields
    op.drop_index('ix_users_classroom_id', table_name='users')
    op.drop_constraint('fk_users_classroom_id', 'users', type_='foreignkey')
    op.drop_column('users', 'classroom_id')

    op.drop_index('ix_users_grade_id', table_name='users')
    op.drop_constraint('fk_users_grade_id', 'users', type_='foreignkey')
    op.drop_column('users', 'grade_id')

    op.drop_index('ix_users_region_id', table_name='users')
    op.drop_constraint('fk_users_region_id', 'users', type_='foreignkey')
    op.drop_column('users', 'region_id')
