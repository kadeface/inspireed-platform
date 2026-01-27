# 多数据库共享快速开始指南

## 📋 方案概述

**推荐方案**: PostgreSQL Schema 隔离
- ✅ **简单**: 同一数据库实例，使用 Schema 实现逻辑隔离
- ✅ **高效**: 支持跨 Schema JOIN 查询，性能影响 <5%
- ✅ **可靠**: 保证事务一致性（ACID）
- ✅ **灵活**: 易于添加新应用

## 🏗️ 架构设计

```
PostgreSQL 数据库 (inspireed)
├── shared (共享数据)          ← 用户、学校、班级等
│   ├── users
│   ├── regions
│   ├── schools
│   ├── classrooms
│   ├── subjects
│   └── grades
├── inspireed (InspireEd 业务) ← 课程、活动等
│   ├── lessons
│   ├── cells
│   ├── activities
│   └── ...
└── app2 (应用2 业务)          ← 未来应用
    └── ...
```

## 🚀 快速实施步骤

### 1. 创建 Schema

```sql
-- 连接到数据库
psql -h localhost -U postgres -d inspireed

-- 创建 Schema
CREATE SCHEMA IF NOT EXISTS shared;
CREATE SCHEMA IF NOT EXISTS inspireed;
CREATE SCHEMA IF NOT EXISTS app2;
```

### 2. 迁移现有表到对应 Schema

```sql
-- 移动共享表（按依赖顺序）
ALTER TABLE regions SET SCHEMA shared;
ALTER TABLE schools SET SCHEMA shared;
ALTER TABLE classrooms SET SCHEMA shared;
ALTER TABLE subjects SET SCHEMA shared;
ALTER TABLE grades SET SCHEMA shared;
ALTER TABLE users SET SCHEMA shared;

-- 移动 InspireEd 业务表
ALTER TABLE lessons SET SCHEMA inspireed;
ALTER TABLE cells SET SCHEMA inspireed;
-- ... 其他业务表
```

### 3. 更新模型定义

```python
# 共享模型
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "shared"}  # 指定 Schema
    # ...

# InspireEd 业务模型
class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = {"schema": "inspireed"}  # 指定 Schema
    
    creator_id = Column(
        Integer, 
        ForeignKey("shared.users.id"),  # 跨 Schema 外键
        nullable=False
    )
    # ...
```

### 4. 更新数据库连接配置

```python
# backend/app/core/config.py
@property
def DATABASE_URI(self) -> str:
    base_uri = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # 设置搜索路径
    search_path = "shared,inspireed,public"
    search_path_encoded = search_path.replace(",", "%2C")
    
    return f"{base_uri}?options=-csearch_path%3D{search_path_encoded}"
```

### 5. 运行 Alembic 迁移

```bash
cd backend
alembic upgrade head
```

## 📝 SQLTools 配置

已经在 `.vscode/settings.json` 中配置好，支持查看多个 Schema：

```json
{
  "sqltools.connections": [{
    "name": "InspireEd PostgreSQL (Docker)",
    "driver": "PostgreSQL",
    "server": "localhost",
    "port": 5432,
    "database": "inspireed",
    "username": "postgres",
    "password": "postgres"
  }]
}
```

在 SQLTools 中可以：
- 查看 `shared` schema 的共享表
- 查看 `inspireed` schema 的业务表
- 查看 `app2` schema 的未来应用表

## 🔍 查询示例

### 跨 Schema 查询

```python
# 查询课程及其创建者（跨 Schema JOIN）
from sqlalchemy import select
from app.models.lesson import Lesson
from app.models.shared.user import User

stmt = (
    select(Lesson, User)
    .join(User, Lesson.creator_id == User.id)
    .where(User.role == "teacher")
)
result = await db.execute(stmt)
```

### 同 Schema 内查询

```python
# 查询课程及其单元（同 Schema）
stmt = (
    select(Lesson)
    .options(selectinload(Lesson.cells))
    .where(Lesson.status == "published")
)
```

## ⚠️ 注意事项

1. **外键约束**: 跨 Schema 外键必须使用完整路径
   - ✅ `ForeignKey("shared.users.id")`
   - ❌ `ForeignKey("users.id")`

2. **模型导入**: 从正确的包导入
   - `from app.models.shared.user import User`
   - `from app.models.lesson import Lesson`

3. **搜索路径**: 在连接字符串中设置，SQLAlchemy 会自动使用

4. **事务**: 跨 Schema 操作在同一事务中，保证一致性

## 📚 详细文档

- **架构设计**: `docs/MULTI_DATABASE_SHARING_DESIGN.md`
- **实施示例**: `docs/SCHEMA_ISOLATION_EXAMPLE.md`
- **迁移脚本**: `backend/alembic/versions/EXAMPLE_add_schema_isolation.py`

## ❓ 常见问题

**Q: 如果应用2需要完全独立的数据库？**  
A: 可以使用方案三（共享数据库 + 独立数据库），迁移成本较低。

**Q: 跨 Schema 查询性能如何？**  
A: 性能影响 <5%，可以忽略不计。跨 Schema JOIN 与同 Schema JOIN 几乎相同。

**Q: 如何添加新的应用？**  
A: 创建新的 Schema，在该 Schema 中创建表，引用 `shared` schema 的共享表即可。

**Q: 能否回滚？**  
A: 可以。将表移回 `public` schema，删除创建的 Schema 即可。见示例迁移脚本的 `downgrade()` 函数。

## 🎯 下一步

1. 阅读详细架构设计文档
2. 根据示例迁移脚本创建实际迁移
3. 更新所有模型定义
4. 测试跨 Schema 查询
5. 部署到生产环境

---

**需要帮助？** 查看详细文档或联系开发团队。
