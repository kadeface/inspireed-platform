# 多数据库共享架构设计文档

## 需求场景

- **应用A**: InspireEd 教育平台（现有）
- **应用B**: 另一个应用（待开发）
- **共享需求**: 两个应用需要共享部分数据（如用户信息、组织架构等）
- **隔离需求**: 每个应用需要有自己的业务数据，保持相对独立

## 方案对比

### 方案一：PostgreSQL Schema 隔离（推荐⭐⭐⭐⭐⭐）

**架构**: 同一数据库实例，使用 Schema 实现逻辑隔离

```
PostgreSQL (inspireed)
├── shared_schema (共享数据)
│   ├── users (用户)
│   ├── regions (区域)
│   ├── schools (学校)
│   ├── classrooms (班级)
│   └── subjects (学科)
├── inspireed_schema (InspireEd 业务数据)
│   ├── lessons (课程)
│   ├── cells (单元)
│   ├── activities (活动)
│   └── ...
└── app2_schema (应用2 业务数据)
    ├── ...
```

**优点**:
- ✅ 易于实现和维护
- ✅ 共享数据天然可见，无需跨数据库查询
- ✅ 支持跨 Schema JOIN 查询
- ✅ 事务一致性保证（ACID）
- ✅ 性能好，无需网络通信
- ✅ 备份和恢复简单

**缺点**:
- ❌ 同一数据库实例，资源竞争
- ❌ Schema 级别的权限控制较复杂

**适用场景**: 
- 共享数据较多，且需要频繁 JOIN 查询
- 需要强一致性的事务保证
- 两个应用部署在同一环境

---

### 方案二：跨数据库 Foreign Data Wrapper (FDW)

**架构**: 两个独立数据库，使用 PostgreSQL FDW 实现跨库查询

```
数据库A (inspireed)
├── shared_schema (共享数据)
│   ├── users
│   ├── schools
│   └── ...
└── inspireed_schema (业务数据)

数据库B (app2)
├── shared_schema (通过 FDW 映射到数据库A)
└── app2_schema (业务数据)
```

**优点**:
- ✅ 完全独立的数据库实例
- ✅ 资源隔离，互不影响
- ✅ 可以独立扩展和备份
- ✅ 支持跨库查询（通过 FDW）

**缺点**:
- ❌ FDW 配置较复杂
- ❌ 跨库查询性能略低
- ❌ 需要手动同步共享数据，或使用 FDW 实时查询
- ❌ 跨库事务一致性难以保证

**适用场景**:
- 两个应用需要完全独立部署
- 共享数据较少，主要是读取操作
- 需要独立扩展数据库资源

---

### 方案三：共享数据库 + 独立数据库（混合方案）

**架构**: 一个共享数据库 + 各自独立的业务数据库

```
共享数据库 (shared_db)
├── users
├── regions
├── schools
└── classrooms

数据库A (inspireed) - InspireEd 业务
├── lessons
├── cells
└── activities

数据库B (app2) - 应用2 业务
└── ...
```

**优点**:
- ✅ 职责清晰：共享数据和业务数据分离
- ✅ 应用独立性强，业务数据库可独立扩展
- ✅ 共享数据集中管理

**缺点**:
- ❌ 需要管理多个数据库连接
- ❌ 跨库 JOIN 查询需要通过应用层实现
- ❌ 事务一致性需要分布式事务支持（如 XA）

**适用场景**:
- 共享数据和应用数据边界清晰
- 两个应用需要完全独立扩展
- 共享数据主要是基础数据（用户、组织等）

---

### 方案四：API 服务共享

**架构**: 通过 API 网关/服务共享数据

```
共享服务 (Shared Service)
├── 用户服务 API
├── 组织架构服务 API
└── ...

应用A (InspireEd)
└── 自己的数据库 + 调用共享服务 API

应用B (App2)
└── 自己的数据库 + 调用共享服务 API
```

**优点**:
- ✅ 完全解耦，服务独立
- ✅ 易于扩展和版本控制
- ✅ 可以使用不同的数据库技术
- ✅ 符合微服务架构

**缺点**:
- ❌ 开发复杂度高
- ❌ 网络延迟
- ❌ 需要处理服务降级和容错
- ❌ 数据一致性需要额外保证（最终一致性）

**适用场景**:
- 大规模微服务架构
- 多个应用需要共享数据
- 需要支持不同技术栈

---

### 方案五：事件驱动同步

**架构**: 使用消息队列（Kafka）同步共享数据

```
共享数据库 (Shared DB)
├── users
└── schools

Kafka 消息队列
├── user.created
├── user.updated
└── school.created

应用A 数据库 (inspireed)
└── users 副本 (通过 Kafka 同步)

应用B 数据库 (app2)
└── users 副本 (通过 Kafka 同步)
```

**优点**:
- ✅ 高可用性和容错性
- ✅ 最终一致性
- ✅ 支持异步处理
- ✅ 易于扩展

**缺点**:
- ❌ 架构复杂
- ❌ 数据延迟
- ❌ 需要处理消息丢失和重复
- ❌ 运维成本高

**适用场景**:
- 大数据量和高并发场景
- 对实时性要求不高
- 需要支持最终一致性

---

## 推荐方案：方案一（PostgreSQL Schema 隔离）

基于 InspireEd 平台的实际情况，推荐使用 **PostgreSQL Schema 隔离方案**，原因：

1. **共享数据较多**: 用户、学校、班级等都是核心共享数据
2. **查询需求**: 业务查询经常需要关联用户和组织信息
3. **一致性要求**: 用户信息的更新需要立即生效
4. **实施简单**: 改动最小，风险最低

## 实施方案

### 第一步：创建共享 Schema

```sql
-- 创建共享 Schema
CREATE SCHEMA IF NOT EXISTS shared;

-- 将共享表移动到 shared schema
ALTER TABLE users SET SCHEMA shared;
ALTER TABLE regions SET SCHEMA shared;
ALTER TABLE schools SET SCHEMA shared;
ALTER TABLE classrooms SET SCHEMA shared;
ALTER TABLE subjects SET SCHEMA shared;
ALTER TABLE grades SET SCHEMA shared;
```

### 第二步：创建应用 Schema

```sql
-- 创建 InspireEd Schema
CREATE SCHEMA IF NOT EXISTS inspireed;

-- 移动 InspireEd 业务表
ALTER TABLE lessons SET SCHEMA inspireed;
ALTER TABLE cells SET SCHEMA inspireed;
ALTER TABLE activities SET SCHEMA inspireed;
-- ... 其他业务表
```

### 第三步：更新 SQLAlchemy 模型

```python
# backend/app/models/user.py
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "shared"}  # 指定 Schema
    
    # ... 字段定义
```

```python
# backend/app/models/lesson.py
from app.core.database import Base

class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = {"schema": "inspireed"}  # 指定 Schema
    
    # 外键引用共享 Schema 的表
    creator_id = Column(Integer, ForeignKey("shared.users.id"), nullable=False)
```

### 第四步：更新数据库连接配置

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # 默认 Schema
    POSTGRES_DEFAULT_SCHEMA: str = "inspireed"
    POSTGRES_SHARED_SCHEMA: str = "shared"
    
    @property
    def DATABASE_URI(self) -> str:
        # 在连接字符串中指定默认 Schema
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}?options=-csearch_path%3D{self.POSTGRES_SHARED_SCHEMA},{self.POSTGRES_DEFAULT_SCHEMA},public"
```

### 第五步：更新 Docker Compose 配置（为应用2准备）

```yaml
# docker/docker-compose.yml
services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    container_name: inspireed-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: inspireed
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    command: 
      - "postgres"
      - "-c"
      - "search_path=shared,inspireed,public"  # 设置默认搜索路径
```

### 第六步：创建应用2的 Schema

当需要添加应用2时：

```sql
-- 创建应用2的 Schema
CREATE SCHEMA IF NOT EXISTS app2;

-- 应用2的表都在 app2 schema 中
CREATE TABLE app2.some_table (...);

-- 如果需要引用共享数据
CREATE TABLE app2.user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES shared.users(id),  -- 引用共享表的用户
    ...
);
```

---

## 迁移步骤

### 阶段一：准备阶段（不影响现有功能）

1. 创建共享 Schema 和 InspireEd Schema
2. 更新所有模型的 `__table_args__` 指定 Schema
3. 更新数据库连接配置，设置搜索路径

### 阶段二：迁移现有表

1. 使用 Alembic 迁移脚本将表移动到对应的 Schema
2. 测试所有功能确保正常工作

### 阶段三：添加应用2

1. 创建应用2的 Schema
2. 应用2访问共享 Schema 的数据
3. 应用2的业务表放在自己的 Schema 中

---

## 常见问题

### Q1: 如何查询跨 Schema 的数据？

```python
# 自动处理（如果设置了 search_path）
user = session.query(User).filter(User.id == user_id).first()  # 从 shared.users 查询

# 显式指定 Schema
from sqlalchemy import Table, MetaData
metadata = MetaData(schema="shared")
users_table = Table("users", metadata, autoload_with=engine)
```

### Q2: 如何保证外键关系？

```python
# 外键需要指定完整的 Schema 路径
class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = {"schema": "inspireed"}
    
    creator_id = Column(
        Integer, 
        ForeignKey("shared.users.id"),  # 完整路径
        nullable=False
    )
```

### Q3: 如何在不同应用间共享数据？

```python
# 应用2 中引用共享数据
from app.shared_models import User  # 导入共享模型

class App2Model(Base):
    __tablename__ = "app2_model"
    __table_args__ = {"schema": "app2"}
    
    user_id = Column(Integer, ForeignKey("shared.users.id"))
    user = relationship("User")  # 需要正确配置 relationship
```

### Q4: 性能影响？

- Schema 隔离对性能影响很小（<5%）
- 跨 Schema JOIN 查询性能与同 Schema 几乎相同
- 可以创建跨 Schema 的索引优化查询

---

## SQLTools 配置更新

更新 `.vscode/settings.json` 以支持多 Schema：

```json
{
  "sqltools.connections": [
    {
      "name": "InspireEd PostgreSQL (Docker)",
      "driver": "PostgreSQL",
      "server": "localhost",
      "port": 5432,
      "database": "inspireed",
      "username": "postgres",
      "password": "postgres",
      "connectionTimeout": 30,
      "connectString": "postgresql://postgres:postgres@localhost:5432/inspireed",
      "previewLimit": 50,
      "schema": ["shared", "inspireed", "app2"]  // 指定要显示的 Schema
    }
  ]
}
```

---

## 总结

对于 InspireEd 平台的多应用共享数据需求，**PostgreSQL Schema 隔离方案**是最佳选择：

- ✅ **简单**: 改动最小，风险最低
- ✅ **高效**: 性能影响可忽略不计
- ✅ **灵活**: 支持跨 Schema 查询和事务
- ✅ **可扩展**: 易于添加新的应用 Schema

如果未来需要完全独立的数据库实例，可以迁移到**方案三（共享数据库 + 独立数据库）**，迁移成本也相对较低。
