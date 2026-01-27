"""Add student_id_number to users

Revision ID: add_student_id_number_to_users
Revises: add_last_login_to_users
Create Date: 2025-12-21 17:23:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "add_student_id_number_to_users"
down_revision: Union[str, None] = "add_last_login_to_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add student_id_number column to users table"""
    
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if column already exists
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'student_id_number' not in columns:
            op.add_column(
                'users',
                sa.Column('student_id_number', sa.String(50), nullable=True, comment='学籍号/身份证号等唯一标识')
            )
            # Create unique index
            op.create_index('ix_users_student_id_number', 'users', ['student_id_number'], unique=True)


def downgrade() -> None:
    """Remove student_id_number column from users table"""
    
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if column exists before removing
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'student_id_number' in columns:
            # Drop index first
            try:
                op.drop_index('ix_users_student_id_number', table_name='users')
            except:
                pass
            op.drop_column('users', 'student_id_number')

