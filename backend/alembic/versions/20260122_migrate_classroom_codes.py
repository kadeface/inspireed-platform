"""migrate classroom codes

Revision ID: 20260122_migrate_classroom_codes
Revises: 20260122_add_seat_number
Create Date: 2026-01-22 09:00:00.000000

This migration converts classroom codes from old format (e.g., "701" = 7th grade class 01)
to new format (e.g., "2301" = 2023 enrollment class 01).

The new format eliminates grade information from classroom codes, removing redundancy
with the grade_id field.

Format: enrollment_year suffix (2 digits) + class sequence (2 digits)

Note: Actual data migration is handled by scripts/migrate_classroom_codes.py
To rollback, restore from backup taken before migration.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260122_migrate_classroom_codes'
down_revision = '20260122_add_seat_number'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Data migration handled by scripts/migrate_classroom_codes.py

    To apply the migration:
        1. Backup your database
        2. Run: python -m scripts.migrate_classroom_codes
    """
    # Data migration handled by external script
    # This serves as a reference marker in the migration chain
    pass


def downgrade() -> None:
    """
    To rollback this migration:
        1. Restore database from backup taken before running the migration script
        2. Mark this migration as complete: alembic downgrade 20260122_migrate_classroom_codes
    """
    # To rollback, restore from backup
    pass
