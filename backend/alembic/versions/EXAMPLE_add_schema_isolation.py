"""add schema isolation (示例迁移脚本)

这是一个示例迁移脚本，展示如何实现 Schema 隔离。
在实际使用时，请根据实际情况调整表名和 Schema 名称。

Revision ID: EXAMPLE_add_schema_isolation
Revises: <latest_revision>
Create Date: 2025-01-XX

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "EXAMPLE_add_schema_isolation"
down_revision = None  # 替换为最新的 revision ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    创建 Schema 并迁移现有表
    
    步骤：
    1. 创建 shared schema（共享数据）
    2. 创建 inspireed schema（InspireEd 业务数据）
    3. 创建 app2 schema（应用2 业务数据，可选）
    4. 将表移动到对应的 Schema
    """
    
    # 步骤1: 创建 Schema
    op.execute("CREATE SCHEMA IF NOT EXISTS shared")
    op.execute("CREATE SCHEMA IF NOT EXISTS inspireed")
    op.execute("CREATE SCHEMA IF NOT EXISTS app2")
    
    # 步骤2: 移动共享表到 shared schema
    # 注意：需要按照外键依赖顺序移动
    shared_tables = [
        "regions",      # 无外键依赖
        "schools",      # 依赖 regions
        "classrooms",   # 依赖 schools
        "subjects",     # 独立表
        "grades",       # 独立表
        "users",        # 依赖 regions, schools, classrooms, grades
    ]
    
    for table_name in shared_tables:
        # 检查表是否存在
        result = op.get_bind().execute(sa.text(
            f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')"
        ))
        if result.scalar():
            op.execute(f'ALTER TABLE {table_name} SET SCHEMA shared')
    
    # 步骤3: 移动 InspireEd 业务表到 inspireed schema
    inspireed_tables = [
        "courses",           # 可能依赖 subjects
        "chapters",          # 依赖 courses
        "lessons",           # 依赖 chapters, users
        "cells",             # 依赖 lessons
        "activities",        # 依赖 lessons, users
        "library_assets",    # 依赖 schools, users, subjects, grades
        "learning_paths",    # 依赖 users
        "student_projects",  # 依赖 users
        "questions",         # 依赖 lessons, cells, users
        "answers",           # 依赖 questions, users
        "reviews",           # 依赖 lessons, users
        "favorites",         # 依赖 lessons, users
        # ... 其他 InspireEd 业务表
    ]
    
    for table_name in inspireed_tables:
        result = op.get_bind().execute(sa.text(
            f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')"
        ))
        if result.scalar():
            op.execute(f'ALTER TABLE {table_name} SET SCHEMA inspireed')
    
    # 步骤4: 更新外键约束以使用正确的 Schema 路径
    # PostgreSQL 会自动处理外键的 Schema 路径，但我们需要确保索引也正确
    
    # 步骤5: 设置默认搜索路径（可选，也可以在连接字符串中设置）
    op.execute("ALTER DATABASE inspireed SET search_path TO shared, inspireed, public")
    
    # 步骤6: 为应用2准备（如果需要）
    # app2 的表将在应用2的迁移脚本中创建
    # 这里只创建空的 Schema 即可


def downgrade() -> None:
    """
    回滚：将表移回 public schema
    """
    
    # 获取所有在 inspireed schema 中的表
    result = op.get_bind().execute(sa.text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'inspireed'
    """))
    inspireed_tables = [row[0] for row in result]
    
    # 先移动业务表（避免外键约束问题）
    for table_name in inspireed_tables:
        op.execute(f'ALTER TABLE inspireed.{table_name} SET SCHEMA public')
    
    # 获取所有在 shared schema 中的表
    result = op.get_bind().execute(sa.text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'shared'
    """))
    shared_tables = [row[0] for row in result]
    
    # 按照依赖关系的反向顺序移动共享表
    # users 应该最后移动（因为它依赖其他表）
    shared_tables_ordered = []
    if "users" in shared_tables:
        shared_tables.remove("users")
        shared_tables_ordered = shared_tables + ["users"]
    else:
        shared_tables_ordered = shared_tables
    
    for table_name in shared_tables_ordered:
        op.execute(f'ALTER TABLE shared.{table_name} SET SCHEMA public')
    
    # 删除 Schema（需要先确保所有表都已移出）
    op.execute("DROP SCHEMA IF EXISTS app2")
    op.execute("DROP SCHEMA IF EXISTS inspireed")
    op.execute("DROP SCHEMA IF EXISTS shared")
    
    # 恢复默认搜索路径
    op.execute("ALTER DATABASE inspireed SET search_path TO public")
