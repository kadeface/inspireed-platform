"""merge cell_uuid and teacher_classrooms migrations

Revision ID: e8232dde319d
Revises: add_cell_uuid_to_submissions, f7g8h9i0j1k2
Create Date: 2025-12-05 02:08:25.811066+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8232dde319d'
down_revision = ('add_cell_uuid_to_submissions', 'f7g8h9i0j1k2')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

