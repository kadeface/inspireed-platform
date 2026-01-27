"""merge 018 and merge_subjects_cell_uuid

Revision ID: 97119fda8aae
Revises: 018, merge_subjects_cell_uuid
Create Date: 2025-12-13 03:09:21.881446+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97119fda8aae'
down_revision = ('018', 'merge_subjects_cell_uuid')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

