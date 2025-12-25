"""merge student_projects and session_id_to_formative_assessments

Revision ID: 4eac54cf4de2
Revises: 20250122_add_student_projects, add_session_id_to_formative_assessments
Create Date: 2025-12-25 22:19:19.065744+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4eac54cf4de2'
down_revision = ('20250122_add_student_projects', 'add_session_id_to_formative_assessments')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

