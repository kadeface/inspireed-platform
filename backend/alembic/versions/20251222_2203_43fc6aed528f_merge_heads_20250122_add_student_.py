"""Merge heads 20250122_add_student_projects and 8c3f5604e35d

Revision ID: 43fc6aed528f
Revises: 20250122_add_student_projects, 8c3f5604e35d
Create Date: 2025-12-22 22:03:50.719147+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43fc6aed528f'
down_revision = ('20250122_add_student_projects', '8c3f5604e35d')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

