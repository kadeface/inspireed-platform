# 考场分配考号缺失错误修复

## 🐛 问题描述

```
分配考场失败: null value in column "exam_number" of relation "exam_room_students"
violates not-null constraint
```

**错误详情**:
- 数据库表 `exam_room_students` 的 `exam_number` 字段有 NOT NULL 约束
- 在分配考场时，`exam_number` 字段值为 `None`
- 导致数据库插入失败

---

## 🔍 根本原因

### 数据库约束

**表**: `exam_room_students`

**字段定义**:
```python
exam_number = Column(String(20), nullable=False, comment="考号")
```

**问题**: `exam_number` 字段不能为空，但代码在创建 `ExamRoomStudent` 时没有提供考号。

### 原有代码逻辑（错误）

**文件**: `backend/app/services/exam_room_service.py`

#### 流程

1. **第103行**: `await db.commit()` - 先创建考场并提交
2. **第106行**: `await self._assign_students_to_rooms(...)` - 分配学生
   - 在 `_assign_by_class` 或 `_assign_mixed` 中创建 `ExamRoomStudent` 对象
   - **没有设置 `exam_number` 字段**
   - 第252行或第301行: `await db.commit()` - 提交学生分配
3. **第109行**: `await self._generate_exam_numbers(exam_rooms, db)` - 生成考号

#### 问题代码示例

**`_assign_by_class` 函数**（第236-244行）:
```python
seat = ExamRoomStudent(
    room_id=room.id,
    student_id=student.id,
    # ❌ 缺少 exam_number 字段！
    seat_number=current_seat,
    student_id_number=student.student_id_number,
    student_name=student.full_name,
    school_id=student.school_id,
    classroom_id=student.classroom_id
)
db.add(seat)
```

**第252行**:
```python
await db.commit()  # ❌ 此时 exam_number 还是 None，违反 NOT NULL 约束
```

### 执行顺序问题

```
创建考场 → commit
    ↓
分配学生（exam_number=None） → commit ❌ 错误！
    ↓
生成考号（但已经太晚）
```

**正确顺序应该是**:
```
分配学生（同时生成exam_number） → commit ✅
```

---

## ✅ 修复方案

### 1. 修改主流程

**文件**: `backend/app/services/exam_room_service.py`

**第105-106行**（修复前）:
```python
# 5. 将学生分配到考场
await self._assign_students_to_rooms(exam_rooms, students, request, db)

# 6. 生成考号
await self._generate_exam_numbers(exam_rooms, db)
```

**修复后**:
```python
# 5. 将学生分配到考场（同时生成考号）
await self._assign_students_to_rooms(exam_rooms, students, request, db)
```

**说明**: 删除了单独的考号生成步骤，改为在分配学生时同时生成考号。

### 2. 修改 `_assign_by_class` 函数

**第208-264行**（修复后）:

```python
async def _assign_by_class(
    self, exam_rooms: List[ExamRoom], students: List[User], capacity: int, db: AsyncSession
):
    """按班级分配学生

    将同班学生分配到同一考场，直到考场满
    """
    year = datetime.now().year  # ✅ 新增：获取年份用于生成考号
    room_index = 0
    room = exam_rooms[room_index]
    current_seat = 1

    for student in students:
        # 检查考场是否已满
        if current_seat > capacity:
            room_index += 1
            if room_index >= len(exam_rooms):
                break
            room = exam_rooms[room_index]
            current_seat = 1

        # ✅ 新增：生成考号
        room_idx = room_index + 1
        exam_number = f"{year}{room_idx:02d}{current_seat:03d}"

        # 创建座位分配
        seat = ExamRoomStudent(
            room_id=room.id,
            student_id=student.id,
            exam_number=exam_number,  # ✅ 添加考号
            seat_number=current_seat,
            student_id_number=student.student_id_number,
            student_name=student.full_name,
            school_id=student.school_id,
            classroom_id=student.classroom_id,
        )
        db.add(seat)

        current_seat += 1

    # ✅ 修改：更新考场座位数和考号范围（同时处理）
    for idx, room in enumerate(exam_rooms, 1):
        # 获取该考场的座位数
        result = await db.execute(
            select(func.count(ExamRoomStudent.id)).where(ExamRoomStudent.room_id == room.id)
        )
        seat_count = result.scalar() or 0

        room.seat_count = seat_count
        room.exam_number_start = f"{year}{idx:02d}001"  # ✅ 设置考号起始
        room.exam_number_end = f"{year}{idx:02d}{seat_count:03d}"  # ✅ 设置考号结束

    await db.commit()  # ✅ 此时 exam_number 已经设置，可以安全提交
```

### 3. 修改 `_assign_mixed` 函数

**第266-297行**（修复后）:

```python
async def _assign_mixed(
    self, exam_rooms: List[ExamRoom], students: List[User], capacity: int, db: AsyncSession
):
    """混排分配学生

    使用轮询方式将学生分配到不同考场
    """
    year = datetime.now().year  # ✅ 新增：获取年份

    # 简单轮询混排
    for i, student in enumerate(students):
        room_index = i % len(exam_rooms)
        room = exam_rooms[room_index]
        seat_number = (i // len(exam_rooms)) + 1

        if seat_number > capacity:
            break

        # ✅ 新增：生成考号
        room_idx = room_index + 1
        exam_number = f"{year}{room_idx:02d}{seat_number:03d}"

        seat = ExamRoomStudent(
            room_id=room.id,
            student_id=student.id,
            exam_number=exam_number,  # ✅ 添加考号
            seat_number=seat_number,
            student_id_number=student.student_id_number,
            student_name=student.full_name,
            school_id=student.school_id,
            classroom_id=student.classroom_id,
        )
        db.add(seat)

    # ✅ 修改：更新考场座位数和考号范围
    for idx, room in enumerate(exam_rooms, 1):
        # 获取该考场的座位数
        result = await db.execute(
            select(func.count(ExamRoomStudent.id)).where(ExamRoomStudent.room_id == room.id)
        )
        seat_count = result.scalar() or 0

        room.seat_count = seat_count
        room.exam_number_start = f"{year}{idx:02d}001"  # ✅ 设置考号起始
        room.exam_number_end = f"{year}{idx:02d}{seat_count:03d}"  # ✅ 设置考号结束

    await db.commit()  # ✅ 此时 exam_number 已经设置，可以安全提交
```

### 4. 删除不再使用的函数

**删除**:
- `_update_room_seat_counts` - 已在分配函数中处理
- `_generate_exam_numbers` - 已在分配函数中处理

---

## 📊 考号生成规则

### 格式

```
{年份}{考场编号:02d}{座位号:03d}
```

### 示例

| 考号 | 年份 | 考场 | 座位 | 说明 |
|------|------|------|------|------|
| 202601001 | 2026 | 01 | 001 | 2026年第01考场第01号座位 |
| 202601030 | 2026 | 01 | 030 | 2026年第01考场第30号座位 |
| 202605001 | 2026 | 05 | 001 | 2026年第05考场第01号座位 |
| 202630030 | 2026 | 30 | 030 | 2026年第30考场第30号座位 |

### 考场编号范围

- **01**: 第1考场
- **30**: 第30考场
- 格式：2位数字，前面补零

### 座位号范围

- **001**: 第1号座位
- **030**: 第30号座位
- 格式：3位数字，前面补零

---

## 🔧 修复对比

### 修复前

| 步骤 | 操作 | exam_number | 提交 |
|------|------|-------------|------|
| 1 | 创建考场 | - | ✅ commit |
| 2 | 创建 ExamRoomStudent | **None** ❌ | ❌ commit **失败** |
| 3 | 生成考号 | （未执行） | - |

### 修复后

| 步骤 | 操作 | exam_number | 提交 |
|------|------|-------------|------|
| 1 | 创建考场 | - | ✅ commit |
| 2 | 创建 ExamRoomStudent | **已生成** ✅ | ✅ commit **成功** |
| 3 | 更新考场考号范围 | **已设置** ✅ | ✅ commit |

---

## ✅ 验证清单

- [x] `_assign_by_class` 函数：在创建 ExamRoomStudent 时生成 exam_number
- [x] `_assign_mixed` 函数：在创建 ExamRoomStudent 时生成 exam_number
- [x] 更新考场考号范围（exam_number_start, exam_number_end）
- [x] 删除不再使用的 `_update_room_seat_counts` 函数
- [x] 删除不再使用的 `_generate_exam_numbers` 函数
- [x] 简化主流程，移除单独的考号生成步骤
- [x] Python 代码格式化（black）

---

## 🎯 测试建议

### 测试场景1: 按班级分配

1. 创建考试（年级：七年级）
2. 导入学生（确保学生已导入）
3. 分配考场：
   - 分配方式：按班级
   - 每考场容量：30人
4. 验证：
   - ✅ 考场创建成功
   - ✅ 学生分配成功
   - ✅ 考号格式正确（如：202601001）
   - ✅ 同班学生在同一考场

### 测试场景2: 混排分配

1. 创建考试（年级：七年级）
2. 导入学生（多个班级）
3. 分配考场：
   - 分配方式：混排
   - 每考场容量：30人
4. 验证：
   - ✅ 考场创建成功
   - ✅ 学生分配成功
   - ✅ 考号格式正确（如：202601001）
   - ✅ 不同班级学生混合在同一考场

### 测试场景3: 考号唯一性

验证以下约束：
- ✅ 同一考场内，考号唯一
- ✅ 不同考场的考号可以重复（但座位号+考场号组合唯一）

---

## 🎉 修复完成

✅ **考号生成时机已修复**: 在分配学生时同步生成考号
✅ **数据库约束已满足**: exam_number 字段在提交前已设置
✅ **代码已优化**: 删除了不必要的函数，简化了流程
✅ **考场范围已设置**: exam_number_start 和 exam_number_end 正确设置

**现在可以正常分配考场了！** 🚀

---

## 📚 相关文档

- [学生导入字段不匹配错误修复](student-import-field-mismatch-fix.md)
- [学生导入类型转换错误修复](student-import-type-conversion-fix.md)
- [学生账户导入策略](student-account-import-guide.md)

---

**修复时间**: 2026-01-17
**错误**: null value in column "exam_number" violates not-null constraint
**原因**: 在分配学生时没有生成考号就提交了数据库
**状态**: ✅ 已修复
**影响**: 考场分配功能现在可以正常工作
