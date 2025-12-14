"""merge subjects and cell_uuid branches

Revision ID: merge_subjects_cell_uuid
Revises: add_cell_uuid_to_submissions, f7e8d9c0b1a2
Create Date: 2025-01-02 00:00:01.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_subjects_cell_uuid'
down_revision = ('add_cell_uuid_to_submissions', 'f7e8d9c0b1a2')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Merge the two branches"""
    pass


def downgrade() -> None:
    """Merge point - no downgrade needed"""
    pass
