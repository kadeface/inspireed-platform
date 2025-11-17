"""merge_classroom_session_and_celltype_fix

Revision ID: 57a9a465710d
Revises: 016_add_classroom_session, 2e224926b436
Create Date: 2025-11-17 04:27:24.424509+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57a9a465710d'
down_revision = ('016_add_classroom_session', '2e224926b436')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

