"""Fix lesson enum values to match SQLAlchemy model

This migration ensures that the lessonstatus enum in PostgreSQL uses lowercase
values that match the Python enum definition in the SQLAlchemy model.

Revision ID: 007
Revises: 006
Create Date: 2025-11-07

"""

from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "007_fix_lesson_enum"
down_revision: Union[str, None] = "006_learning_science"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Fix the lessonstatus enum to use lowercase values.
    
    The Python enum LessonStatus is defined with lowercase values:
    - DRAFT = "draft"
    - PUBLISHED = "published"  
    - ARCHIVED = "archived"
    
    This migration ensures the PostgreSQL enum matches these values.
    """
    
    # Note: This migration is idempotent - if the enum is already correct, it will not cause errors
    
    # Remove default temporarily
    op.execute("ALTER TABLE lessons ALTER COLUMN status DROP DEFAULT")
    
    # Convert column to text type
    op.execute("ALTER TABLE lessons ALTER COLUMN status TYPE VARCHAR USING status::text")
    
    # Drop old enum type if it exists
    op.execute("DROP TYPE IF EXISTS lessonstatus CASCADE")
    
    # Create enum with correct lowercase values
    op.execute("CREATE TYPE lessonstatus AS ENUM ('draft', 'published', 'archived')")
    
    # Convert column back to enum type
    op.execute("ALTER TABLE lessons ALTER COLUMN status TYPE lessonstatus USING LOWER(status)::lessonstatus")
    
    # Restore default
    op.execute("ALTER TABLE lessons ALTER COLUMN status SET DEFAULT 'draft'::lessonstatus")


def downgrade() -> None:
    """
    Revert to uppercase enum values (if needed for compatibility).
    """
    
    # Remove default
    op.execute("ALTER TABLE lessons ALTER COLUMN status DROP DEFAULT")
    
    # Convert to text
    op.execute("ALTER TABLE lessons ALTER COLUMN status TYPE VARCHAR USING status::text")
    
    # Drop lowercase enum
    op.execute("DROP TYPE IF EXISTS lessonstatus CASCADE")
    
    # Create with uppercase values
    op.execute("CREATE TYPE lessonstatus AS ENUM ('DRAFT', 'PUBLISHED', 'ARCHIVED')")
    
    # Convert back with uppercase transformation
    op.execute("ALTER TABLE lessons ALTER COLUMN status TYPE lessonstatus USING UPPER(status)::lessonstatus")
    
    # Restore default
    op.execute("ALTER TABLE lessons ALTER COLUMN status SET DEFAULT 'DRAFT'::lessonstatus")

