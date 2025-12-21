"""Add last_login to users

Revision ID: add_last_login_to_users
Revises: add_classroom_assistant_tables
Create Date: 2025-12-21 00:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "add_last_login_to_users"
down_revision: Union[str, None] = "add_classroom_assistant_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add last_login column to users table"""
    
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if column already exists
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'last_login' not in columns:
            op.add_column(
                'users',
                sa.Column('last_login', sa.DateTime(), nullable=True, comment='最后登录时间')
            )


def downgrade() -> None:
    """Remove last_login column from users table"""
    
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if column exists before removing
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'last_login' in columns:
            op.drop_column('users', 'last_login')

