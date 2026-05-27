"""merge image_cell and whiteboard migration heads

Revision ID: 20260526_merge_heads
Revises: 20260426_image_cell, 20260526_whiteboard
Create Date: 2026-05-26
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260526_merge_heads"
down_revision: Union[str, tuple[str, ...], None] = (
    "20260426_image_cell",
    "20260526_whiteboard",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
