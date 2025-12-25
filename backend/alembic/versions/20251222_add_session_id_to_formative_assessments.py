"""add session_id to formative_assessments

Revision ID: add_session_id_to_formative_assessments
Revises: add_student_id_number_to_users
Create Date: 2025-12-22 00:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "add_session_id_to_formative_assessments"
down_revision: Union[str, None] = "add_student_id_number_to_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add session_id column to formative_assessments table and update unique constraint"""
    
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if table exists
    if 'formative_assessments' not in inspector.get_table_names():
        return
    
    # Check if column already exists
    columns = [col['name'] for col in inspector.get_columns('formative_assessments')]
    
    # Drop existing unique constraint
    constraints = inspector.get_unique_constraints('formative_assessments')
    for constraint in constraints:
        if constraint['name'] == 'uq_formative_assessment_scope':
            op.drop_constraint('uq_formative_assessment_scope', 'formative_assessments', type_='unique')
            break
    
    # Add session_id column if it doesn't exist
    if 'session_id' not in columns:
        op.add_column(
            'formative_assessments',
            sa.Column('session_id', sa.Integer(), nullable=True)
        )
        
        # Add foreign key constraint
        op.create_foreign_key(
            'fk_formative_assessments_session_id',
            'formative_assessments',
            'class_sessions',
            ['session_id'],
            ['id'],
            ondelete='CASCADE'
        )
    
    # Create index on session_id
    indexes = [idx['name'] for idx in inspector.get_indexes('formative_assessments')]
    if 'ix_formative_assessments_session_id' not in indexes:
        op.create_index(
            'ix_formative_assessments_session_id',
            'formative_assessments',
            ['session_id']
        )
    
    # Recreate unique constraint with session_id
    op.create_unique_constraint(
        'uq_formative_assessment_scope',
        'formative_assessments',
        ['lesson_id', 'student_id', 'phase', 'session_id']
    )


def downgrade() -> None:
    """Remove session_id column from formative_assessments table"""
    
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if table exists
    if 'formative_assessments' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('formative_assessments')]
    
    # Drop unique constraint
    constraints = inspector.get_unique_constraints('formative_assessments')
    for constraint in constraints:
        if constraint['name'] == 'uq_formative_assessment_scope':
            op.drop_constraint('uq_formative_assessment_scope', 'formative_assessments', type_='unique')
            break
    
    # Drop index
    indexes = [idx['name'] for idx in inspector.get_indexes('formative_assessments')]
    if 'ix_formative_assessments_session_id' in indexes:
        op.drop_index('ix_formative_assessments_session_id', table_name='formative_assessments')
    
    # Drop foreign key constraint
    foreign_keys = inspector.get_foreign_keys('formative_assessments')
    for fk in foreign_keys:
        if fk['name'] == 'fk_formative_assessments_session_id':
            op.drop_constraint('fk_formative_assessments_session_id', 'formative_assessments', type_='foreignkey')
            break
    
    # Drop column
    if 'session_id' in columns:
        op.drop_column('formative_assessments', 'session_id')
    
    # Recreate original unique constraint without session_id
    op.create_unique_constraint(
        'uq_formative_assessment_scope',
        'formative_assessments',
        ['lesson_id', 'student_id', 'phase']
    )

