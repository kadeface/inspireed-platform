"""fix class session status enum: PENDING/ACTIVE/PAUSED/ENDED -> PREPARING/TEACHING/ENDED

Revision ID: 20260202_fix_enum
Revises: 20260131_1400
Create Date: 2026-02-02

The Python model ClassSessionStatus uses PREPARING, TEACHING, ENDED.
The database enum used PENDING, ACTIVE, PAUSED, ENDED. This migration
aligns the database with the Python model (v2 classroom session design).

Mapping:
- PENDING -> PREPARING (准备中)
- ACTIVE -> TEACHING (上课中)
- PAUSED -> TEACHING (暂停视为上课中)
- ENDED -> ENDED
"""
from alembic import op

revision = '20260202_fix_enum'
down_revision = '20260131_1400'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Create new enum with PREPARING, TEACHING, ENDED
    op.execute("""
        CREATE TYPE classsessionstatus_new AS ENUM ('PREPARING', 'TEACHING', 'ENDED');
    """)

    # Step 2: Alter column, mapping old values to new
    op.execute("""
        ALTER TABLE class_sessions
        ALTER COLUMN status TYPE classsessionstatus_new
        USING CASE status::text
            WHEN 'PENDING' THEN 'PREPARING'::text
            WHEN 'ACTIVE' THEN 'TEACHING'::text
            WHEN 'PAUSED' THEN 'TEACHING'::text
            WHEN 'ENDED' THEN 'ENDED'::text
            ELSE 'PREPARING'::text
        END::classsessionstatus_new;
    """)

    # Step 3: Drop old type
    op.execute("DROP TYPE classsessionstatus;")

    # Step 4: Rename new type
    op.execute("ALTER TYPE classsessionstatus_new RENAME TO classsessionstatus;")


def downgrade() -> None:
    # Recreate old enum
    op.execute("""
        CREATE TYPE classsessionstatus_old AS ENUM ('PENDING', 'ACTIVE', 'PAUSED', 'ENDED');
    """)

    op.execute("""
        ALTER TABLE class_sessions
        ALTER COLUMN status TYPE classsessionstatus_old
        USING CASE status::text
            WHEN 'PREPARING' THEN 'PENDING'::text
            WHEN 'TEACHING' THEN 'ACTIVE'::text
            WHEN 'ENDED' THEN 'ENDED'::text
            ELSE 'PENDING'::text
        END::classsessionstatus_old;
    """)

    op.execute("DROP TYPE classsessionstatus;")
    op.execute("ALTER TYPE classsessionstatus_old RENAME TO classsessionstatus;")
