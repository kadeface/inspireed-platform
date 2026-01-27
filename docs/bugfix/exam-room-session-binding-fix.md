# 考场分配Session绑定错误修复

## 🐛 问题描述

```
Internal server error: Instance <ExamRoom at 0x12e7479d0> is not bound to a Session;
attribute refresh operation cannot proceed
```

**错误详情**:
- SQLAlchemy ORM 对象 `ExamRoom` 在序列化时访问了懒加载的关系属性
- 对象没有绑定到活跃的数据库会话
- 导致无法加载关系数据

---

## 🔍 根本原因

### 问题分析

**文件**: `backend/app/api/v1/exam_rooms.py`

**原始代码**（第80-81行）:
```python
rooms = await service.auto_assign_rooms(exam_id, request, db)
return rooms  # ❌ 直接返回 ORM 对象
```

### 为什么会出错？

1. **ORM 对象的懒加载**
   - `ExamRoom` 模型定义了关系属性：
   ```python
   students = relationship("ExamRoomStudent", back_populates="exam_room")
   proctors = relationship("ExamProctor", back_populates="exam_room")
   ```

2. **响应模型要求关系数据**
   - `ExamRoomResponse` 包含：
   ```python
   students: List[ExamRoomStudentResponse] = []
   proctors: List[ExamProctorResponse] = []
   ```

3. **序列化时访问关系**
   - FastAPI 尝试序列化 `ExamRoom` 对象
   - Pydantic 访问 `students` 和 `proctors` 属性
   - SQLAlchemy 尝试从数据库加载这些关系
   - **但此时对象可能已经脱离了原始会话**

4. **会话生命周期问题**
   ```
   auto_assign_rooms() → 创建对象 → commit → 返回对象
                                                         ↓
                                                    API 返回
                                                         ↓
                                                  Pydantic 序列化
                                                         ↓
                                                  访问懒加载属性 ❌
                                                         ↓
                                            Session 已关闭/不存在
   ```

---

## ✅ 修复方案

### 解决策略

**在返回前重新查询并预加载所有关系**

**文件**: `backend/app/api/v1/exam_rooms.py`

**修复后代码**（第74-101行）:

```python
# 自动分配考场
service = ExamRoomService()
try:
    rooms = await service.auto_assign_rooms(exam_id, request, db)

    # 重新查询考场以预加载所有关系
    from sqlalchemy.orm import selectinload
    from app.models.exam_room import ExamRoom

    room_ids = [r.id for r in rooms]
    result = await db.execute(
        select(ExamRoom)
        .options(
            selectinload(ExamRoom.students),  # 预加载学生关系
            selectinload(ExamRoom.proctors),  # 预加载监考关系
        )
        .where(ExamRoom.id.in_(room_ids))
    )
    loaded_rooms = result.scalars().all()

    # 按原始顺序排序
    room_dict = {r.id: r for r in loaded_rooms}
    ordered_rooms = [room_dict[rid] for rid in room_ids if rid in room_dict]

    return ordered_rooms  # ✅ 返回预加载了关系的对象
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e)
    )
```

### 修复说明

#### 1. 重新查询对象

```python
room_ids = [r.id for r in rooms]  # 提取已创建考场的ID
```

**目的**: 获取刚创建的考场的ID列表

#### 2. 预加载关系

```python
result = await db.execute(
    select(ExamRoom)
    .options(
        selectinload(ExamRoom.students),  # 预加载学生
        selectinload(ExamRoom.proctors),  # 预加载监考
    )
    .where(ExamRoom.id.in_(room_ids))
)
```

**关键点**:
- `selectinload(ExamRoom.students)`: 告诉 SQLAlchemy 在查询时立即加载 students 关系
- `selectinload(ExamRoom.proctors)`: 告诉 SQLAlchemy 在查询时立即加载 proctors 关系
- **避免后续的懒加载操作**

#### 3. 保持顺序

```python
room_dict = {r.id: r for r in loaded_rooms}
ordered_rooms = [room_dict[rid] for rid in room_ids if rid in room_dict]
```

**目的**: 确保返回的考场列表顺序与创建时一致

---

## 📊 修复对比

### 修复前

```
auto_assign_rooms() 创建考场
    ↓
返回 ORM 对象（关系未加载）
    ↓
FastAPI 序列化
    ↓
Pydantic 访问 .students, .proctors
    ↓
SQLAlchemy 尝试懒加载 ❌
    ↓
错误：Instance is not bound to a Session
```

### 修复后

```
auto_assign_rooms() 创建考场
    ↓
重新查询（使用 selectinload）
    ↓
预加载所有关系 ✅
    ↓
返回 ORM 对象（关系已加载）
    ↓
FastAPI 序列化
    ↓
Pydantic 访问 .students, .proctors
    ↓
使用已加载的数据 ✅
    ↓
成功返回响应
```

---

## 🔧 SQLAlchemy 预加载策略

### selectinload vs joinedload

#### selectinload（推荐）

```python
select(ExamRoom).options(
    selectinload(ExamRoom.students)
)
```

**特点**:
- 发送 **2 条查询**（1条查询考场，1条查询学生）
- 适用于 **一对多** 关系
- 不会导致笛卡尔积
- **性能更可预测**

#### joinedload

```python
select(ExamRoom).options(
    joinedload(ExamRoom.students)
)
```

**特点**:
- 发送 **1 条查询**（使用 JOIN）
- 可能导致结果集重复
- 需要使用 `.unique()` 去重
- 适用于 **多对一** 和 **一对一** 关系

### 为什么使用 selectinload？

```python
# ExamRoom 与 ExamRoomStudent 是一对多关系
class ExamRoom(Base):
    students = relationship("ExamRoomStudent")  # 一个考场多个学生
```

**选择**:
- ✅ `selectinload` - 适合一对多
- ❌ `joinedload` - 可能导致重复数据

---

## ✅ 验证清单

- [x] 在返回前重新查询 ExamRoom 对象
- [x] 使用 selectinload 预加载 students 关系
- [x] 使用 selectinload 预加载 proctors 关系
- [x] 保持返回列表的原始顺序
- [x] Python 代码格式化（black）

---

## 🎯 测试建议

### 测试场景1: 正常分配考场

1. 创建考试
2. 导入学生
3. 分配考场：
   ```
   POST /api/v1/exams/{exam_id}/rooms/auto-assign
   {
     "capacity_per_room": 30,
     "arrangement_type": "by_class",
     "seat_pattern": "s_shape",
     "use_existing_rooms": true
   }
   ```

**预期结果**:
- ✅ 返回考场列表
- ✅ 每个考场包含 students 数组
- ✅ 每个考场包含 proctors 数组（即使为空）
- ✅ 没有 Session 错误

### 测试场景2: 验证关系数据

检查响应数据：

```json
[
  {
    "id": 1,
    "name": "第1考场",
    "students": [
      {
        "id": 1,
        "exam_number": "202601001",
        "student_name": "张三"
      }
    ],
    "proctors": []
  }
]
```

---

## 🎉 修复完成

✅ **Session 绑定问题已修复**: 在返回前重新查询并预加载关系
✅ **懒加载问题已解决**: 使用 selectinload 立即加载关系数据
✅ **响应格式正确**: ExamRoomResponse 可以正确序列化
✅ **性能优化**: 预加载避免了 N+1 查询问题

**现在可以正常返回考场数据了！** 🚀

---

## 📚 相关文档

- [考场分配考号缺失错误修复](exam-room-assignment-exam-number-fix.md)
- [学生导入字段不匹配错误修复](student-import-field-mismatch-fix.md)
- [SQLAlchemy Documentation - Loading Strategies](https://docs.sqlalchemy.org/en/20/orm/loading_relationships.html)

---

**修复时间**: 2026-01-17
**错误**: Instance is not bound to a Session
**原因**: ORM 对象在序列化时访问了懒加载关系，但 Session 已不可用
**状态**: ✅ 已修复
**影响**: 考场分配 API 现在可以正常返回完整的考场数据
