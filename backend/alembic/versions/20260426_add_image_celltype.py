"""add IMAGE to celltype enum

Revision ID: 20260426_image_cell
Revises: 20260405_guest_session
Create Date: 2026-04-26

Adds IMAGE cell type for lesson/project image cells (PostgreSQL celltype enum).
"""
from typing import Sequence, Union

from alembic import op


revision: str = "20260426_image_cell"
down_revision: Union[str, None] = "20260405_guest_session"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type DROP DEFAULT")
    op.execute("ALTER TABLE project_cells ALTER COLUMN cell_type DROP DEFAULT")

    op.execute("ALTER TYPE celltype RENAME TO celltype_old")

    op.execute(
        """
        CREATE TYPE celltype AS ENUM (
            'ACTIVITY',
            'BROWSER',
            'CHART',
            'CODE',
            'CONTEST',
            'FLOWCHART',
            'IMAGE',
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
    """
    )

    op.execute(
        """
        ALTER TABLE cells
        ALTER COLUMN cell_type
        TYPE celltype
        USING cell_type::text::celltype
    """
    )

    op.execute(
        """
        ALTER TABLE project_cells
        ALTER COLUMN cell_type
        TYPE celltype
        USING cell_type::text::celltype
    """
    )

    op.execute("ALTER TABLE cells ALTER COLUMN cell_type SET DEFAULT 'TEXT'")

    op.execute("DROP TYPE celltype_old")


def downgrade() -> None:
    op.execute("ALTER TABLE cells ALTER COLUMN cell_type DROP DEFAULT")
    op.execute("ALTER TABLE project_cells ALTER COLUMN cell_type DROP DEFAULT")

    op.execute(
        """
        UPDATE cells SET cell_type = 'TEXT'::celltype WHERE cell_type::text = 'IMAGE'
    """
    )
    op.execute(
        """
        UPDATE project_cells SET cell_type = 'TEXT'::celltype WHERE cell_type::text = 'IMAGE'
    """
    )

    op.execute("ALTER TYPE celltype RENAME TO celltype_old")

    op.execute(
        """
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
    """
    )

    op.execute(
        """
        ALTER TABLE cells
        ALTER COLUMN cell_type
        TYPE celltype
        USING cell_type::text::celltype
    """
    )

    op.execute(
        """
        ALTER TABLE project_cells
        ALTER COLUMN cell_type
        TYPE celltype
        USING cell_type::text::celltype
    """
    )

    op.execute("ALTER TABLE cells ALTER COLUMN cell_type SET DEFAULT 'TEXT'")

    op.execute("DROP TYPE celltype_old")
