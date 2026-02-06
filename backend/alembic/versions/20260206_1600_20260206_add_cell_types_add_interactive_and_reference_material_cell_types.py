"""add_interactive_and_reference_material_cell_types

Revision ID: 20260206_add_cell_types
Revises: d2f64fcf0f31
Create Date: 2026-02-06 16:00:00.000000+00:00

Add INTERACTIVE and REFERENCE_MATERIAL to celltype enum.
These types are used in frontend but missing from backend.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260206_add_cell_types'
down_revision = 'd2f64fcf0f31'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add INTERACTIVE and REFERENCE_MATERIAL to celltype enum"""

    # Step 1: Remove default values from all tables using celltype
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type DROP DEFAULT")
    op.execute("ALTER TABLE project_cells ALTER COLUMN cell_type DROP DEFAULT")

    # Step 2: Rename old enum type
    op.execute("ALTER TYPE celltype RENAME TO celltype_old")

    # Step 3: Create new enum type with new values
    op.execute("""
        CREATE TYPE celltype AS ENUM (
            'ACTIVITY',
            'BROWSER',
            'CHART',
            'CODE',
            'CONTEST',
            'FLOWCHART',
            'INTERACTIVE',
            'QA',
            'REFERENCE_MATERIAL',
            'SIM',
            'TEXT',
            'VIDEO',
            'activity',
            'browser',
            'flowchart'
        )
    """)

    # Step 4: Convert columns to new type (for both tables)
    op.execute("""
        ALTER TABLE cells
        ALTER COLUMN cell_type
        TYPE celltype
        USING cell_type::text::celltype
    """)

    op.execute("""
        ALTER TABLE project_cells
        ALTER COLUMN cell_type
        TYPE celltype
        USING cell_type::text::celltype
    """)

    # Step 5: Set back default values
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type SET DEFAULT 'TEXT'")

    # Step 6: Drop old enum type
    op.execute("DROP TYPE celltype_old")


def downgrade() -> None:
    """Remove INTERACTIVE and REFERENCE_MATERIAL from celltype enum"""

    # Step 1: Remove default values
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type DROP DEFAULT")
    op.execute("ALTER TABLE project_cells ALTER COLUMN cell_type DROP DEFAULT")

    # Step 2: Rename current enum type
    op.execute("ALTER TYPE celltype RENAME TO celltype_old")

    # Step 3: Create new enum type without the new values
    op.execute("""
        CREATE TYPE celltype AS ENUM (
            'ACTIVITY',
            'BROWSER',
            'CHART',
            'CODE',
            'CONTEST',
            'FLOWCHART',
            'QA',
            'SIM',
            'TEXT',
            'VIDEO',
            'activity',
            'browser',
            'flowchart'
        )
    """)

    # Step 4: Convert columns back to old type (for both tables)
    op.execute("""
        ALTER TABLE cells
        ALTER COLUMN cell_type
        TYPE celltype
        USING cell_type::text::celltype
    """)

    op.execute("""
        ALTER TABLE project_cells
        ALTER COLUMN cell_type
        TYPE celltype
        USING cell_type::text::celltype
    """)

    # Step 5: Set back default values
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type SET DEFAULT 'TEXT'")

    # Step 6: Drop old enum type
    op.execute("DROP TYPE celltype_old")
