"""remove course subject/grade unique constraint

Revision ID: c9e2f8a1d5ef
Revises: b2e6f4321abc
Create Date: 2025-11-10 09:00:00.000000+00:00

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "c9e2f8a1d5ef"
down_revision = "b2e6f4321abc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("uix_subject_grade", "courses", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("uix_subject_grade", "courses", ["subject_id", "grade_id"])

