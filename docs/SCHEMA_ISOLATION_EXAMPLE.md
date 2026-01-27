# Schema 隔离实施示例

## 快速开始

本文档提供实施 Schema 隔离的具体代码示例。

## 1. 更新模型定义

### 共享模型（Shared Schema）

```python
# backend/app/models/shared/user.py
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    """用户模型 - 共享数据"""
    
    __tablename__ = "users"
    __table_args__ = {"schema": "shared"}  # 指定 Schema
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 外键引用 shared schema 中的其他表
    region_id = Column(
        Integer, 
        ForeignKey("shared.regions.id"),  # 需要指定完整路径
        nullable=True
    )
    school_id = Column(
        Integer, 
        ForeignKey("shared.schools.id"),
        nullable=True
    )
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    region = relationship("Region", foreign_keys=[region_id])
    school = relationship("School", foreign_keys=[school_id])


class Region(Base):
    """区域模型 - 共享数据"""
    
    __tablename__ = "regions"
    __table_args__ = {"schema": "shared"}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    level = Column(Integer, nullable=False)
    parent_id = Column(
        Integer, 
        ForeignKey("shared.regions.id"),  # 自引用也需要完整路径
        nullable=True
    )


class School(Base):
    """学校模型 - 共享数据"""
    
    __tablename__ = "schools"
    __table_args__ = {"schema": "shared"}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    region_id = Column(
        Integer, 
        ForeignKey("shared.regions.id"),
        nullable=False
    )
```

### InspireEd 业务模型（InspireEd Schema）

```python
# backend/app/models/lesson.py
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

class Lesson(Base):
    """课程模型 - InspireEd 业务数据"""
    
    __tablename__ = "lessons"
    __table_args__ = {"schema": "inspireed"}  # 指定 Schema
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 外键引用 shared schema 中的用户表
    creator_id = Column(
        Integer, 
        ForeignKey("shared.users.id"),  # 跨 Schema 引用需要完整路径
        nullable=False,
        index=True
    )
    
    status = Column(String(50), default="draft", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    creator = relationship(
        "User",  # 从 shared schema 导入
        foreign_keys=[creator_id],
        lazy="select"  # 跨 Schema 查询建议使用 select 加载策略
    )


class Cell(Base):
    """单元模型 - InspireEd 业务数据"""
    
    __tablename__ = "cells"
    __table_args__ = {"schema": "inspireed"}
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(
        Integer, 
        ForeignKey("inspireed.lessons.id"),  # 同 Schema 内的表可以省略 Schema
        nullable=False,
        index=True
    )
    cell_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=True)
    
    # 关联关系
    lesson = relationship("Lesson", back_populates="cells")
```

## 2. 更新数据库连接配置

```python
# backend/app/core/config.py
from pydantic import BaseSettings, field_validator
from typing import Optional

class Settings(BaseSettings):
    # ... 其他配置 ...
    
    # Schema 配置
    POSTGRES_DEFAULT_SCHEMA: str = "inspireed"
    POSTGRES_SHARED_SCHEMA: str = "shared"
    
    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "inspireed"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URI(self) -> str:
        """
        构建数据库连接字符串，包含搜索路径
        
        搜索路径顺序：
        1. shared - 共享数据（优先级最高）
        2. inspireed - InspireEd 业务数据
        3. public - 默认 Schema
        """
        base_uri = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
        # 设置搜索路径（options 参数）
        search_path = f"{self.POSTGRES_SHARED_SCHEMA},{self.POSTGRES_DEFAULT_SCHEMA},public"
        # URL 编码：空格 -> %20, 逗号 -> %2C
        search_path_encoded = search_path.replace(",", "%2C").replace(" ", "%20")
        
        return f"{base_uri}?options=-csearch_path%3D{search_path_encoded}"


# 使用示例
settings = Settings()
print(settings.DATABASE_URI)
# 输出: postgresql+asyncpg://postgres:postgres@localhost:5432/inspireed?options=-csearch_path%3Dshared%2Cinspireed%2Cpublic
```

## 3. 查询示例

### 跨 Schema 查询

```python
# backend/app/api/endpoints/lessons.py
from sqlalchemy.orm import Session
from app.models.lesson import Lesson
from app.models.shared.user import User  # 从 shared 导入

async def get_lesson_with_creator(lesson_id: int, db: AsyncSession):
    """获取课程及其创建者信息"""
    
    # 方式1: 使用 relationship（推荐）
    lesson = await db.get(Lesson, lesson_id)
    if lesson:
        # 会自动加载 creator（因为设置了 relationship）
        creator_name = lesson.creator.full_name if lesson.creator else None
        return lesson
    
    # 方式2: 手动 JOIN 查询
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    stmt = (
        select(Lesson)
        .options(selectinload(Lesson.creator))  # 预加载关联对象
        .where(Lesson.id == lesson_id)
    )
    result = await db.execute(stmt)
    lesson = result.scalar_one_or_none()
    
    return lesson


async def get_user_lessons(user_id: int, db: AsyncSession):
    """获取用户创建的所有课程"""
    
    from sqlalchemy import select
    
    # 查询 inspireed schema 中的课程，过滤创建者为指定用户
    stmt = (
        select(Lesson)
        .where(Lesson.creator_id == user_id)  # 跨 Schema 外键查询
        .order_by(Lesson.created_at.desc())
    )
    result = await db.execute(stmt)
    lessons = result.scalars().all()
    
    return lessons


async def get_lessons_with_school_info(region_id: int, db: AsyncSession):
    """获取某个区域下所有学校的课程（需要跨 Schema JOIN）"""
    
    from sqlalchemy import select
    from app.models.shared.school import School
    from app.models.shared.user import User
    
    # 跨 Schema JOIN 查询
    stmt = (
        select(Lesson, User, School)
        .join(User, Lesson.creator_id == User.id)  # JOIN shared.users
        .join(School, User.school_id == School.id)  # JOIN shared.schools
        .where(School.region_id == region_id)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    # 处理结果
    lessons = []
    for lesson, user, school in rows:
        lessons.append({
            "lesson": lesson,
            "creator": user,
            "school": school
        })
    
    return lessons
```

## 4. Alembic 迁移示例

参考 `backend/alembic/versions/EXAMPLE_add_schema_isolation.py` 文件。

## 5. 应用2的模型示例

如果未来需要添加应用2，可以这样定义：

```python
# app2/models/user_profile.py
from app.core.database import Base
from app.models.shared.user import User  # 导入共享模型
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class UserProfile(Base):
    """用户资料 - 应用2的业务数据"""
    
    __tablename__ = "user_profiles"
    __table_args__ = {"schema": "app2"}  # 应用2的 Schema
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 引用共享 Schema 中的用户
    user_id = Column(
        Integer, 
        ForeignKey("shared.users.id"),  # 跨 Schema 引用
        nullable=False,
        unique=True,
        index=True
    )
    
    # 应用2特有的字段
    bio = Column(String(500), nullable=True)
    preferences = Column(JSON, nullable=True)
    
    # 关联关系
    user = relationship("User", foreign_keys=[user_id])
```

## 6. 测试 Schema 隔离

```python
# backend/tests/test_schema_isolation.py
import pytest
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

@pytest.mark.asyncio
async def test_schema_isolation():
    """测试 Schema 隔离是否正常工作"""
    
    async with AsyncSessionLocal() as session:
        # 测试1: 查询共享 Schema 中的用户
        result = await session.execute(
            text("SELECT COUNT(*) FROM shared.users")
        )
        user_count = result.scalar()
        assert user_count >= 0
        
        # 测试2: 查询 InspireEd Schema 中的课程
        result = await session.execute(
            text("SELECT COUNT(*) FROM inspireed.lessons")
        )
        lesson_count = result.scalar()
        assert lesson_count >= 0
        
        # 测试3: 跨 Schema JOIN 查询
        result = await session.execute(
            text("""
                SELECT l.id, l.title, u.full_name 
                FROM inspireed.lessons l
                JOIN shared.users u ON l.creator_id = u.id
                LIMIT 1
            """)
        )
        row = result.first()
        if row:
            assert row[0] is not None  # lesson_id
            assert row[1] is not None  # lesson_title
            assert row[2] is not None  # creator_name
        
        # 测试4: 验证搜索路径
        result = await session.execute(
            text("SHOW search_path")
        )
        search_path = result.scalar()
        assert "shared" in search_path
        assert "inspireed" in search_path

@pytest.mark.asyncio
async def test_cross_schema_foreign_key():
    """测试跨 Schema 外键关系"""
    
    from app.models.lesson import Lesson
    from app.models.shared.user import User
    
    async with AsyncSessionLocal() as session:
        # 创建测试用户（在 shared schema）
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
            role="teacher"
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        
        # 创建测试课程（在 inspireed schema，引用 shared 的用户）
        test_lesson = Lesson(
            title="Test Lesson",
            creator_id=test_user.id  # 跨 Schema 外键
        )
        session.add(test_lesson)
        await session.commit()
        await session.refresh(test_lesson)
        
        # 验证关联关系
        assert test_lesson.creator_id == test_user.id
        
        # 清理
        await session.delete(test_lesson)
        await session.delete(test_user)
        await session.commit()
```

## 7. 注意事项

### 外键约束

- 跨 Schema 外键必须使用完整的表路径：`ForeignKey("shared.users.id")`
- 同 Schema 内可以省略：`ForeignKey("lessons.id")` 或 `ForeignKey("inspireed.lessons.id")`

### 索引

- 跨 Schema 的索引创建需要指定 Schema
- 外键自动创建的索引会在正确的 Schema 中

### 事务

- 跨 Schema 操作在同一事务中，保证 ACID 特性
- 如果某个 Schema 的表操作失败，整个事务回滚

### 性能

- Schema 隔离对性能影响很小（<5%）
- 跨 Schema JOIN 查询性能与同 Schema 几乎相同
- 建议为经常跨 Schema 查询的字段创建索引

## 8. 迁移检查清单

- [ ] 创建 Schema（shared, inspireed, app2）
- [ ] 更新所有模型的 `__table_args__` 指定 Schema
- [ ] 更新所有外键约束使用完整路径
- [ ] 运行 Alembic 迁移脚本
- [ ] 更新数据库连接配置，设置搜索路径
- [ ] 测试所有 API 端点
- [ ] 验证跨 Schema 查询正常工作
- [ ] 更新文档和注释

## 总结

Schema 隔离方案是 PostgreSQL 提供的强大功能，可以：
- ✅ 逻辑隔离不同应用的数据
- ✅ 共享基础数据（用户、组织等）
- ✅ 保持事务一致性
- ✅ 最小化性能影响
- ✅ 易于实施和维护

这是多应用共享数据的理想解决方案！
