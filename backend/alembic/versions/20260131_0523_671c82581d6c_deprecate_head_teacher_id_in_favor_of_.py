"""deprecate head_teacher_id and deputy_head_teacher_id fields

Revision ID: 671c82581d6c
Revises: 20260131_fix_session_enum
Create Date: 2026-01-31

This migration:
1. Migrates existing head_teacher_id data to ClassroomMembership
2. Adds deprecation comments to the fields
3. Does NOT remove the fields (for backward compatibility)

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '671c82581d6c'
down_revision = '20260131_fix_session_enum'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Migrate head_teacher_id to ClassroomMembership"""
    conn = op.get_bind()

    # Step 1: Migrate existing head_teacher_id to ClassroomMembership
    conn.execute(sa.text("""
        INSERT INTO classroom_memberships (classroom_id, user_id, role_in_class, is_active, is_primary_class, created_at, updated_at)
        SELECT id, head_teacher_id, 'head_teacher_primary', true, false, NOW(), NOW()
        FROM classrooms
        WHERE head_teacher_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM classroom_memberships
            WHERE classroom_id = classrooms.id
            AND user_id = classrooms.head_teacher_id
            AND role_in_class = 'head_teacher_primary'
        )
    """))

    # Migrate deputy_head_teacher_id
    conn.execute(sa.text("""
        INSERT INTO classroom_memberships (classroom_id, user_id, role_in_class, is_active, is_primary_class, created_at, updated_at)
        SELECT id, deputy_head_teacher_id, 'head_teacher_deputy', true, false, NOW(), NOW()
        FROM classrooms
        WHERE deputy_head_teacher_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM classroom_memberships
            WHERE classroom_id = classrooms.id
            AND user_id = classrooms.deputy_head_teacher_id
            AND role_in_class = 'head_teacher_deputy'
        )
    """))

    # Step 2: Add deprecation comments (PostgreSQL)
    conn.execute(sa.text("""
        COMMENT ON COLUMN classrooms.head_teacher_id IS 'DEPRECATED: Use ClassroomMembership with role=head_teacher_primary instead. Kept for backward compatibility.'
    """))

    conn.execute(sa.text("""
        COMMENT ON COLUMN classrooms.deputy_head_teacher_id IS 'DEPRECATED: Use ClassroomMembership with role=head_teacher_deputy instead. Kept for backward compatibility.'
    """))


def downgrade() -> None:
    """Reverse migration"""
    conn = op.get_bind()

    # Remove comments
    conn.execute(sa.text("""
        COMMENT ON COLUMN classrooms.head_teacher_id IS '正班主任ID'
    """))

    conn.execute(sa.text("""
        COMMENT ON COLUMN classrooms.deputy_head_teacher_id IS '副班主任ID'
    """))


