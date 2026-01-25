# 增值评价系统权限控制指南

## 📋 概述

本文档详细说明增值评价系统的权限控制机制，包括角色定义、数据访问规则和最佳实践。

## 🔐 角色体系

### 角色定义

增值评价系统使用简化的6种角色，从高到低依次为：

| 角色 | 代码 | 说明 | 数据范围 |
|------|------|------|----------|
| 系统管理员 | `ADMIN` | 超级管理员，拥有所有权限 | 全部数据 |
| 区县管理员 | `DISTRICT_ADMIN` | 区县教育管理人员 | 所属区县 |
| 学校管理员 | `SCHOOL_ADMIN` | 学校管理人员 | 本校 |
| 教研员 | `RESEARCHER` | 教学研究员 | 所属区县/学校 |
| 教师 | `TEACHER` | 任课教师（含班主任） | 所教班级 |
| 学生 | `STUDENT` | 学生 | 个人数据 |

### 权限层级

```
ADMIN (系统管理员)
  └─ 可以访问和管理所有数据
DISTRICT_ADMIN (区县管理员)
  └─ 可以访问和管理所属区县的数据
SCHOOL_ADMIN (学校管理员)
  └─ 可以访问和管理本校的数据
RESEARCHER (教研员)
  └─ 可以查看和创建所属区县/学校的评价
TEACHER (教师)
  └─ 可以查看所教班级的数据
STUDENT (学生)
  └─ 只能查看个人数据，不能访问评价系统
```

## 📊 数据访问权限矩阵

### 区县数据

| 角色 | 访问 | 修改 | 删除 | 说明 |
|------|:----:|:----:|:----:|------|
| ADMIN | ✓ | ✓ | ✓ | 可管理所有区县 |
| DISTRICT_ADMIN | ✓ | ✓ | ✓ | 只能管理所属区县 |
| SCHOOL_ADMIN | ✓ | ✗ | ✗ | 只能查看 |
| RESEARCHER | ✓ | ✗ | ✗ | 只能查看所属区县 |
| TEACHER | ✓ | ✗ | ✗ | 只能查看 |
| STUDENT | ✓ | ✗ | ✗ | 只能查看 |

### 学校数据

| 角色 | 访问 | 修改 | 删除 | 说明 |
|------|:----:|:----:|:----:|------|
| ADMIN | ✓ | ✓ | ✓ | 可管理所有学校 |
| DISTRICT_ADMIN | ✓ | ✓ | ✓ | 可管理所属区县的学校 |
| SCHOOL_ADMIN | ✓ | ✓ | ✓ | 可管理本校 |
| RESEARCHER | ✓ | ✗ | ✗ | 只能查看所属区县/学校 |
| TEACHER | ✓ | ✗ | ✗ | 只能查看本校 |
| STUDENT | ✓ | ✗ | ✗ | 只能查看本校 |

### 班级数据

| 角色 | 访问 | 修改 | 删除 | 说明 |
|------|:----:|:----:|:----:|------|
| ADMIN | ✓ | ✓ | ✓ | 可管理所有班级 |
| DISTRICT_ADMIN | ✓ | ✓ | ✓ | 可管理所属区县的班级 |
| SCHOOL_ADMIN | ✓ | ✓ | ✓ | 可管理本校班级 |
| RESEARCHER | ✓ | ✗ | ✗ | 只能查看所属区县/学校班级 |
| TEACHER | ✓ | ✓ | ✗ | 可管理所教班级 |
| STUDENT | ✓ | ✗ | ✗ | 只能查看所属班级 |

### 评价数据

| 角色 | 访问 | 创建 | 修改 | 删除 | 说明 |
|------|:----:|:----:|:----:|:----:|------|
| ADMIN | ✓ | ✓ | ✓ | ✓ | 所有评价 |
| DISTRICT_ADMIN | ✓ | ✓ | ✓ | ✓ | 所属区县评价 |
| SCHOOL_ADMIN | ✓ | ✓ | ✓ | ✓ | 本校评价 |
| RESEARCHER | ✓ | ✓ | ✓ | ✗ | 所属评价 |
| TEACHER | ✓ | ✗ | ✗ | ✗ | 只能查看 |
| STUDENT | ✗ | ✗ | ✗ | ✗ | 无权访问 |

### 成绩数据

| 角色 | 查看个人 | 查看班级 | 查看学校 | 导入 | 说明 |
|------|:-------:|:-------:|:-------:|:----:|------|
| ADMIN | ✓ | ✓ | ✓ | ✓ | 所有成绩 |
| DISTRICT_ADMIN | ✓ | ✓ | ✓ | ✓ | 所属区县 |
| SCHOOL_ADMIN | ✓ | ✓ | ✓ | ✓ | 本校 |
| RESEARCHER | ✓ | ✓ | ✓ | ✗ | 所属范围 |
| TEACHER | ✓ | ✓ | ✗ | ✗ | 所教班级 |
| STUDENT | ✓ | ✗ | ✗ | ✗ | 仅个人 |

## 🔍 权限检查函数

### 核心权限检查器

`PermissionChecker` 类提供了一系列静态方法用于权限检查：

```python
from app.core.permissions import PermissionChecker

# 检查区县数据访问权限
can_access = await PermissionChecker.can_access_region_data(
    current_user, region_id=1
)

# 检查学校数据修改权限
can_modify = await PermissionChecker.can_modify_school_data(
    current_user, school_id=1
)

# 检查班级数据访问权限
can_access = await PermissionChecker.can_access_classroom_data(
    db, current_user, classroom_id=1
)

# 检查学生数据访问权限
can_access = await PermissionChecker.can_access_student_data(
    db, current_user, student_id=1
)

# 检查评价访问权限
can_access = await PermissionChecker.can_access_evaluation(
    db, current_user, evaluation
)
```

### 权限验证快捷函数

```python
from app.core.permissions import (
    check_permission_or_403,
    require_admin_or_district_admin,
    require_admin_or_school_admin,
    require_management_role,
)

# 检查权限，不满足抛出403异常
await check_permission_or_403(
    can_access=False,
    detail="您没有权限访问此资源"
)

# 要求管理员或区县管理员
await require_admin_or_district_admin(current_user)

# 要求管理员或学校管理员
await require_admin_or_school_admin(current_user)

# 要求管理角色
await require_management_role(current_user)
```

## 💡 使用示例

### 示例1: API端点权限控制

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_active_user
from app.core.permissions import PermissionChecker
from app.models import User

router = APIRouter()

@router.post("/evaluations/")
async def create_evaluation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    evaluation_in: EvaluationCreate,
):
    # 权限检查：只有管理员和教研员可以创建评价
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.DISTRICT_ADMIN,
        UserRole.SCHOOL_ADMIN,
        UserRole.RESEARCHER,
    ]:
        raise HTTPException(status_code=403, detail="权限不足")

    # 检查数据访问权限
    can_create = await PermissionChecker.can_modify_evaluation(
        db, current_user, evaluation
    )
    if not can_create:
        raise HTTPException(status_code=403, detail="只能创建所属范围的")

    # 创建评价...
    return evaluation
```

### 示例2: 在查询中应用权限过滤

```python
@router.get("/evaluations/")
async def list_evaluations(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 构建查询条件
    conditions = []

    # 根据角色限制数据访问
    if current_user.role == UserRole.SCHOOL_ADMIN:
        conditions.append(ValueAddedEvaluation.school_id == current_user.school_id)
    elif current_user.role == UserRole.RESEARCHER:
        if current_user.school_id:
            conditions.append(ValueAddedEvaluation.school_id == current_user.school_id)
        elif current_user.region_id:
            conditions.append(ValueAddedEvaluation.region_id == current_user.region_id)
    elif current_user.role == UserRole.TEACHER:
        # 教师只能查看本校评价
        conditions.append(ValueAddedEvaluation.school_id == current_user.school_id)
    elif current_user.role == UserRole.STUDENT:
        # 学生不能查看评价
        return []

    # 执行查询
    if conditions:
        query = select(ValueAddedEvaluation).where(and_(*conditions))
    else:
        query = select(ValueAddedEvaluation)

    result = await db.execute(query)
    return result.scalars().all()
```

### 示例3: 跨区访问控制

```python
@router.get("/schools/{school_id}/evaluations")
async def get_school_evaluations(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    school_id: int,
):
    # 检查是否可以访问该校数据
    can_access = await PermissionChecker.can_access_school_data(
        current_user, school_id
    )
    if not can_access:
        raise HTTPException(
            status_code=403,
            detail="您没有权限访问该校数据"
        )

    # 查询评价数据...
    evaluations = await get_evaluations_by_school(db, school_id)
    return evaluations
```

## ⚠️ 权限陷阱和最佳实践

### 常见陷阱

1. **只检查角色，不检查数据范围**
   ```python
   # ❌ 错误：只检查角色
   if current_user.role == UserRole.SCHOOL_ADMIN:
       return get_all_evaluations()  # 返回所有评价！

   # ✓ 正确：同时检查角色和数据范围
   if current_user.role == UserRole.SCHOOL_ADMIN:
       return get_evaluations_by_school(current_user.school_id)
   ```

2. **忘记处理管理员角色**
   ```python
   # ❌ 错误：管理员被排除在外
   if current_user.role == UserRole.SCHOOL_ADMIN:
       # 只有学校管理员能访问
       pass

   # ✓ 正确：管理员有最高权限
   if current_user.role in [UserRole.ADMIN, UserRole.SCHOOL_ADMIN]:
       pass
   ```

3. **在查询后检查权限**
   ```python
   # ❌ 错误：先查询后检查（性能差）
   data = await db.execute(select(Score).where(...))
   if not can_access:
       raise HTTPException(403)

   # ✓ 正确：先检查权限再查询
   if not can_access:
       raise HTTPException(403)
   data = await db.execute(select(Score).where(...))
   ```

### 最佳实践

1. **使用权限检查器**
   ```python
   # 推荐使用统一的权限检查器
   can_access = await PermissionChecker.can_access_school_data(
       current_user, school_id
   )
   ```

2. **在SQL层面过滤数据**
   ```python
   # 在查询条件中过滤，避免查询后过滤
   conditions = []
   if current_user.role == UserRole.SCHOOL_ADMIN:
       conditions.append(Score.school_id == current_user.school_id)

   query = select(Score).where(and_(*conditions))
   ```

3. **早期权限验证**
   ```python
   # 在函数开始就检查权限
   @router.post("/evaluations/")
   async def create_evaluation(...):
       # 1. 验证角色
       if current_user.role not in MANAGEABLE_ROLES:
           raise HTTPException(403)

       # 2. 验证数据访问权限
       can_access = await PermissionChecker.can_modify_evaluation(...)
       if not can_access:
           raise HTTPException(403)

       # 3. 执行业务逻辑
       ...
   ```

4. **记录权限拒绝日志**
   ```python
   if not can_access:
       logger.warning(
           f"用户 {current_user.id} ({current_user.role}) "
           f"尝试访问资源 {resource_id} 被拒绝"
       )
       raise HTTPException(403)
   ```

## 🧪 测试权限

### 权限测试框架

系统提供了完整的权限测试框架：

```bash
# 运行权限测试
cd backend
python test_permissions.py
```

测试覆盖：
- ✅ 6种角色的数据访问权限
- ✅ 4种数据类型（区县、学校、班级、学生）
- ✅ 跨区访问控制
- ✅ 权限层级验证

### 测试输出示例

```
场景1: 访问区县数据 (region_id=1)
------------------------------------------------------------
  admin           - 访问: ✓, 修改: ✓
  district_admin  - 访问: ✓, 修改: ✓
  school_admin    - 访问: ✓, 修改: ✗
  researcher      - 访问: ✓, 修改: ✗
  teacher         - 访问: ✓, 修改: ✗
  student         - 访问: ✓, 修改: ✗
```

## 🔗 相关文档

- [API参考文档](./evaluation-api-reference.md)
- [实施进度报告](./implementation-progress-report.md)
- [增值评价计算服务](../app/services/value_added_evaluation_service.py)

---

**文档生成时间**: 2026-01-14
**版本**: v1.0
