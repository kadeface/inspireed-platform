"""fix class session status enum to uppercase

Revision ID: 20260131_fix_session_enum
Revises: 20260123_add_lesson_sections
Create Date: 2026-01-31 12:00:00.000000

This migration fixes the ClassSessionStatus enum to use uppercase values
to match PostgreSQL conventions and resolve the enum mismatch error.

Changes:
- Updates classsessionstatus enum from lowercase ('pending', 'active', 'paused', 'ended')
  to uppercase ('PENDING', 'ACTIVE', 'PAUSED', 'ENDED')
- Ensures consistency between Python Enum and database schema
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260131_fix_session_enum'
down_revision = '20260123_add_lesson_sections'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Create a new enum type with uppercase values
    op.execute("""
        CREATE TYPE classsessionstatus_new AS ENUM ('PENDING', 'ACTIVE', 'PAUSED', 'ENDED');
    """)

    # Step 2: Update the column to use the new type
    # Convert lowercase to uppercase during the conversion
    op.execute("""
        ALTER TABLE class_sessions
        ALTER COLUMN status TYPE classsessionstatus_new
        USING CASE status::text
            WHEN 'pending' THEN 'PENDING'::text
            WHEN 'active' THEN 'ACTIVE'::text
            WHEN 'paused' THEN 'PAUSED'::text
            WHEN 'ended' THEN 'ENDED'::text
            ELSE status::text
        END::classsessionstatus_new;
    """)

    # Step 3: Drop the old type
    op.execute("DROP TYPE classsessionstatus;")

    # Step 4: Rename the new type to the original name
    op.execute("ALTER TYPE classsessionstatus_new RENAME TO classsessionstatus;")


def downgrade() -> None:
    # Reverse the process - go back to lowercase
    op.execute("""
        CREATE TYPE classsessionstatus_new AS ENUM ('pending', 'active', 'paused', 'ended');
    """)

    op.execute("""
        ALTER TABLE class_sessions
        ALTER COLUMN status TYPE classsessionstatus_new
        USING CASE status::text
            WHEN 'PENDING' THEN 'pending'::text
            WHEN 'ACTIVE' THEN 'active'::text
            WHEN 'PAUSED' THEN 'paused'::text
            WHEN 'ENDED' THEN 'ended'::text
            ELSE status::text
        END::classsessionstatus_new;
    """)

    op.execute("DROP TYPE classsessionstatus;")
    op.execute("ALTER TYPE classsessionstatus_new RENAME TO classsessionstatus;")
