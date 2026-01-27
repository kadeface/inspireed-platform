"""add seat_number to users

Revision ID: 20260122_add_seat_number
Revises: 20260118_grade_subject
Create Date: 2026-01-22 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260122_add_seat_number'
down_revision = '20260118_grade_subject'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('seat_number', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'seat_number')
