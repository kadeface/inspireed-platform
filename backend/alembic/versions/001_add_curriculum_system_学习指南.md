# Alembic 迁移文件学习指南：001_add_curriculum_system.py

## 📚 目录
1. [Alembic 迁移文件基本结构](#基本结构)
2. [文件头部和元数据](#文件头部)
3. [upgrade() 函数详解](#upgrade函数)
4. [downgrade() 函数详解](#downgrade函数)
5. [关键概念和最佳实践](#关键概念)
6. [代码逐行解读](#逐行解读)

---

## 基本结构

Alembic 迁移文件通常包含以下部分：

```python
# 1. 文件头注释（描述迁移内容）
# 2. 导入语句
# 3. 版本标识符（revision, down_revision 等）
# 4. upgrade() 函数（向前迁移）
# 5. downgrade() 函数（回滚迁移）
```

---

## 文件头部

### 1. 文档字符串（第 1-7 行）
```python
"""Add curriculum system

Revision ID: 001
Revises:
Create Date: 2025-10-14
"""
```
- **作用**：描述迁移的目的和基本信息
- **Revision ID**：当前迁移的唯一标识符
- **Revises**：此迁移基于哪个迁移（这里是空，因为是第一个迁移）
- **Create Date**：创建日期

### 2. 导入语句（第 9-14 行）
```python
from typing import Sequence, Union
from alembic import op          # Alembic 操作接口
import sqlalchemy as sa          # SQLAlchemy 核心
from sqlalchemy import inspect   # 数据库检查工具
from datetime import datetime
```

**关键导入说明**：
- `op`：Alembic 的操作对象，用于执行数据库操作
- `sa`：SQLAlchemy，用于定义列类型和约束
- `inspect`：检查数据库结构（表、列是否存在）

### 3. 版本标识符（第 17-21 行）
```python
revision: str = "001"                    # 当前迁移的版本号
down_revision: Union[str, None] = None   # 前一个迁移版本（None 表示这是根迁移）
branch_labels: Union[str, Sequence[str], None] = None  # 分支标签
depends_on: Union[str, Sequence[str], None] = None   # 依赖的其他迁移
```

**重要概念**：
- `revision`：必须唯一，用于标识迁移
- `down_revision`：指向父迁移，形成迁移链
  - `None` 表示这是第一个迁移（根节点）
  - 其他迁移会指向前一个迁移的 revision
- `branch_labels`：用于标记分支（如开发分支）
- `depends_on`：用于并行开发的依赖关系

---

## upgrade() 函数

`upgrade()` 函数定义了**向前迁移**的逻辑，即如何将数据库从旧版本升级到新版本。

### 整体流程

```
1. 创建 subjects（学科）表
2. 创建 grades（年级）表
3. 创建 courses（课程）表
4. 插入初始数据（种子数据）
5. 处理 lessons（教案）表（创建或添加字段）
```

### 详细解读

#### 1. 创建 subjects 表（第 27-52 行）

```python
op.create_table(
    "subjects",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("name", sa.String(length=100), nullable=False),
    # ... 更多列
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("name"),
    sa.UniqueConstraint("code"),
)
op.create_index(op.f("ix_subjects_id"), "subjects", ["id"], unique=False)
```

**关键点**：
- `op.create_table()`：创建新表
- `sa.Column()`：定义列
  - `nullable=False`：不允许 NULL
  - `server_default`：数据库层面的默认值
- `sa.PrimaryKeyConstraint()`：主键约束
- `sa.UniqueConstraint()`：唯一约束
- `op.create_index()`：创建索引
  - `op.f("ix_subjects_id")`：生成标准化的索引名称

**列类型说明**：
- `sa.Integer()`：整数
- `sa.String(length=100)`：字符串，最大长度 100
- `sa.Text()`：长文本
- `sa.Boolean()`：布尔值
- `sa.DateTime()`：日期时间

#### 2. 创建 grades 表（第 54-77 行）

类似 subjects 表，存储年级信息（一年级到高三）。

#### 3. 创建 courses 表（第 79-127 行）

```python
op.create_table(
    "courses",
    # ... 列定义
    sa.ForeignKeyConstraint(
        ["subject_id"],
        ["subjects.id"],
    ),
    sa.ForeignKeyConstraint(
        ["grade_id"],
        ["grades.id"],
    ),
    sa.UniqueConstraint("subject_id", "grade_id", name="uix_subject_grade"),
)
```

**外键约束**：
- `ForeignKeyConstraint`：定义外键关系
- `["subject_id"], ["subjects.id"]`：courses.subject_id 引用 subjects.id

**复合唯一约束**：
- `UniqueConstraint("subject_id", "grade_id")`：确保同一学科+年级的组合唯一

**条件性外键创建**（第 117-127 行）：
```python
conn = op.get_bind()
inspector = inspect(conn)
if 'users' in inspector.get_table_names():
    op.create_foreign_key(...)
```

**为什么这样做？**
- 迁移可能在不同环境下运行
- 某些表可能还不存在
- 使用 `inspect` 检查表是否存在，避免错误

#### 4. 插入种子数据（第 129-163 行）

```python
op.execute("""
    INSERT INTO subjects (name, code, description, display_order) VALUES
    ('数学', 'math', '数学学科', 1),
    ('物理', 'physics', '物理学科', 2),
    ...
""")
```

**种子数据的作用**：
- 初始化系统必需的基础数据
- 确保系统有可用的学科和年级数据
- 使用 `op.execute()` 执行原始 SQL

#### 5. 处理 lessons 表（第 165-261 行）

这是最复杂的部分，展示了**条件性表创建**：

```python
if 'lessons' not in inspector.get_table_names():
    # 创建完整的 lessons 表
    op.create_table("lessons", ...)
else:
    # 表已存在，只添加 course_id 列
    existing_columns = [col['name'] for col in inspector.get_columns('lessons')]
    if 'course_id' not in existing_columns:
        op.add_column("lessons", sa.Column("course_id", ...))
```

**为什么需要这种逻辑？**
- 不同环境可能有不同的数据库状态
- 新部署：表不存在，需要创建
- 已有系统：表存在，只需添加字段
- 提高迁移的**幂等性**（可以安全地多次运行）

**枚举类型**（第 184-189 行）：
```python
sa.Column(
    "status",
    sa.Enum("draft", "published", "archived", name="lessonstatus"),
    nullable=False,
    server_default="draft",
)
```

- PostgreSQL 的枚举类型
- 限制值只能是 "draft", "published", "archived"

**自引用外键**（第 243-250 行）：
```python
op.create_foreign_key(
    "fk_lessons_parent_id",
    "lessons",
    "lessons",  # 引用自己
    ["parent_id"],
    ["id"],
)
```

- 用于实现版本控制或层级结构
- parent_id 指向同一表的其他记录

---

## downgrade() 函数

`downgrade()` 函数定义了**回滚迁移**的逻辑，即如何撤销 upgrade() 的更改。

### 执行顺序（与 upgrade 相反）

```
1. 删除 lessons 表的 course_id 相关约束和列
2. 删除 courses 表
3. 删除 grades 表
4. 删除 subjects 表
```

### 错误处理模式（第 271-282 行）

```python
try:
    op.drop_constraint("fk_lessons_course_id", "lessons", type_="foreignkey")
except:
    pass
```

**为什么使用 try-except？**
- 如果约束/索引/列不存在，删除会失败
- 使用异常捕获确保回滚不会因小错误而中断
- **注意**：bare `except:` 在生产代码中不推荐，但迁移场景可接受

**更好的做法**（可选）：
```python
except Exception:
    pass
# 或更具体
except (OperationalError, ProgrammingError):
    pass
```

---

## 关键概念

### 1. 幂等性（Idempotency）

迁移应该可以安全地多次运行。这个文件通过以下方式实现：

- 检查表是否存在：`if 'lessons' not in inspector.get_table_names()`
- 检查列是否存在：`if 'course_id' not in existing_columns`
- 使用 `IF NOT EXISTS` 或异常处理

### 2. 依赖关系管理

- **外键顺序**：先创建被引用的表（subjects, grades），再创建引用表（courses）
- **条件性创建**：检查依赖表是否存在（如 users 表）

### 3. 数据迁移策略

- **种子数据**：使用 `op.execute()` 插入初始数据
- **数据迁移**：如果需要转换现有数据，在 upgrade() 中添加逻辑

### 4. 索引命名规范

```python
op.f("ix_subjects_id")  # 生成 "ix_subjects_id"
```

- Alembic 的命名函数，确保索引名称一致
- 格式：`ix_表名_列名`

---

## 逐行解读（重点部分）

### 创建表的完整示例

```python
op.create_table(
    "subjects",                    # 表名
    sa.Column("id", ...),          # 列定义
    sa.PrimaryKeyConstraint("id"), # 主键
    sa.UniqueConstraint("name"),   # 唯一约束
)
```

### 服务器默认值

```python
sa.Column(
    "is_active",
    sa.Boolean(),
    nullable=False,
    server_default="true"  # 数据库层面的默认值
)
```

- `server_default`：在数据库层面设置默认值
- 与 Python 层面的默认值不同，即使直接插入 SQL 也会生效

### 检查数据库结构

```python
conn = op.get_bind()              # 获取数据库连接
inspector = inspect(conn)          # 创建检查器
tables = inspector.get_table_names()  # 获取所有表名
columns = inspector.get_columns('lessons')  # 获取表的列信息
```

---

## 最佳实践总结

### ✅ 应该做的

1. **检查表/列是否存在**：使用 `inspect` 避免重复创建
2. **按依赖顺序创建**：先创建被引用的表
3. **提供种子数据**：初始化系统必需的数据
4. **实现完整的 downgrade**：确保可以回滚
5. **使用有意义的 revision ID**：便于追踪

### ❌ 避免做的

1. **硬编码假设**：不要假设表一定存在或不存在
2. **忽略错误处理**：downgrade 中要处理可能不存在的对象
3. **破坏性更改**：避免直接删除重要数据
4. **跳过测试**：迁移前在测试环境验证

---

## 学习建议

1. **理解迁移链**：每个迁移都基于前一个迁移
2. **实践操作**：
   ```bash
   # 运行迁移
   alembic upgrade head
   
   # 回滚一个版本
   alembic downgrade -1
   
   # 查看当前版本
   alembic current
   ```

3. **对比 SQLAlchemy 模型**：查看对应的模型定义，理解迁移如何实现模型

4. **阅读其他迁移文件**：了解不同类型的迁移（添加列、修改类型、数据迁移等）

---

## 常见问题

### Q: 为什么有些字段是 nullable=True？
A: 为了兼容性，允许在迁移过程中数据暂时为空，后续迁移可以改为 NOT NULL。

### Q: 什么时候使用 op.execute()？
A: 当需要执行复杂 SQL 或批量操作时，如插入种子数据、数据转换等。

### Q: 如何测试迁移？
A: 在测试数据库上运行 `alembic upgrade head` 和 `alembic downgrade base`，确保可以来回迁移。

---

## 相关资源

- [Alembic 官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 类型系统](https://docs.sqlalchemy.org/en/14/core/type_basics.html)
- [PostgreSQL 数据类型](https://www.postgresql.org/docs/current/datatype.html)
