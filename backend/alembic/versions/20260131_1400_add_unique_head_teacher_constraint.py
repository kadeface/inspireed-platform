"""add unique constraint for head teachers

Revision ID: 20260131_1400
Revises: 20260131_0523
Create Date: 2025-01-31

This migration adds a partial unique index to ensure only one HEAD_TEACHER_PRIMARY
can exist per classroom (when is_active = TRUE).
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260131_1400'
down_revision = '20260131_0523'
branch_labels = None
depends_on = None


def upgrade():
    """Add unique partial index for head teachers"""

    # First, clean up any existing duplicates (keep the first one)
    op.execute("""
        DELETE FROM classroom_memberships
        WHERE id IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (
                    PARTITION BY classroom_id
                    ORDER BY created_at ASC
                ) as row_num
                FROM classroom_memberships
                WHERE role_in_class = 'head_teacher_primary'
                AND is_active = TRUE
            ) sub
            WHERE row_num > 1
        )
    """)

    # Add the unique partial index
    # PostgreSQL syntax for partial unique index
    op.execute("""
        CREATE UNIQUE INDEX uq_classroom_head_teacher
        ON classroom_memberships (classroom_id)
        WHERE role_in_class = 'head_teacher_primary' AND is_active = TRUE
    """)


def downgrade():
    """Remove the unique index"""
    op.execute("DROP INDEX IF EXISTS uq_classroom_head_teacher")
