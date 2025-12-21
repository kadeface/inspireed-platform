"""add student projects

Revision ID: 20250122_add_student_projects
Revises: 20251221_add_last_login_to_users
Create Date: 2025-01-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20250122_add_student_projects"
down_revision = "add_student_id_number_to_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 创建项目状态枚举
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE projectstatus AS ENUM ('draft', 'in_progress', 'completed', 'submitted');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )

    # 2. 创建5E阶段枚举
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE projectstage AS ENUM ('engage', 'explore', 'explain', 'elaborate', 'evaluate');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )

    # 3. 创建学生项目表
    op.create_table(
        "student_projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("project_type", sa.String(50), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "in_progress",
                "completed",
                "submitted",
                name="projectstatus",
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "engage_content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "explore_content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "explain_content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "elaborate_content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "evaluate_content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "completion",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default='{"engage": 0, "explore": 0, "explain": 0, "elaborate": 0, "evaluate": 0}',
        ),
        sa.Column("is_team_project", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "team_members",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("cover_image_url", sa.String(500), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 创建索引
    op.create_index(
        "idx_student_projects_creator", "student_projects", ["creator_id"]
    )
    op.create_index(
        "idx_student_projects_status", "student_projects", ["status"]
    )

    # 4. 创建项目Cell表
    op.create_table(
        "project_cells",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column(
            "stage",
            sa.Enum(
                "engage",
                "explore",
                "explain",
                "elaborate",
                "evaluate",
                name="projectstage",
            ),
            nullable=False,
        ),
        sa.Column(
            "cell_type",
            sa.Enum(
                "TEXT",
                "VIDEO",
                "CODE",
                "SIM",
                "QA",
                "CHART",
                "CONTEST",
                "PARAM",
                "ACTIVITY",
                "FLOWCHART",
                "BROWSER",
                name="celltype",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column(
            "content",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["student_projects.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 创建索引
    op.create_index(
        "idx_project_cells_project", "project_cells", ["project_id"]
    )
    op.create_index(
        "idx_project_cells_stage", "project_cells", ["stage"]
    )
    op.create_index(
        "idx_project_cells_project_stage", "project_cells", ["project_id", "stage"]
    )


def downgrade() -> None:
    # 删除索引
    op.drop_index("idx_project_cells_project_stage", table_name="project_cells")
    op.drop_index("idx_project_cells_stage", table_name="project_cells")
    op.drop_index("idx_project_cells_project", table_name="project_cells")
    op.drop_index("idx_student_projects_status", table_name="student_projects")
    op.drop_index("idx_student_projects_creator", table_name="student_projects")

    # 删除表
    op.drop_table("project_cells")
    op.drop_table("student_projects")

    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS projectstage")
    op.execute("DROP TYPE IF EXISTS projectstatus")

