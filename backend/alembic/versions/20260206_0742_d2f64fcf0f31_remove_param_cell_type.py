"""remove_param_cell_type

Revision ID: d2f64fcf0f31
Revises: 20260202_fix_enum
Create Date: 2026-02-06 07:42:28.817107+00:00

Remove PARAM from celltype enum.
Since PostgreSQL doesn't support removing enum values directly,
we need to recreate the enum type without PARAM.

Note: Both 'cells' and 'project_cells' tables use the celltype enum.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2f64fcf0f31'
down_revision = '20260202_fix_enum'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove PARAM from celltype enum"""

    # Step 1: Remove default values from all tables using celltype
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type DROP DEFAULT")
    op.execute("ALTER TABLE project_cells ALTER COLUMN cell_type DROP DEFAULT")

    # Step 2: Rename old enum type
    op.execute("ALTER TYPE celltype RENAME TO celltype_old")

    # Step 3: Create new enum type without PARAM
    op.execute("""
        CREATE TYPE celltype AS ENUM (
            'ACTIVITY',
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

    # Step 6: Drop old enum type (now safe because both tables converted)
    op.execute("DROP TYPE celltype_old")


def downgrade() -> None:
    """Restore PARAM to celltype enum"""

    # Step 1: Remove default values
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type DROP DEFAULT")
    op.execute("ALTER TABLE project_cells ALTER COLUMN cell_type DROP DEFAULT")

    # Step 2: Rename current enum type
    op.execute("ALTER TYPE celltype RENAME TO celltype_old")

    # Step 3: Create new enum type with PARAM restored
    op.execute("""
        CREATE TYPE celltype AS ENUM (
            'ACTIVITY',
            'CHART',
            'CODE',
            'CONTEST',
            'FLOWCHART',
            'PARAM',
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
