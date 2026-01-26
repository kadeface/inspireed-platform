# 考号使用学号修复

## 🎯 问题说明

**原问题**: 考场安排系统自动生成考号（格式：`{年份}{考场编号:02d}{座位号:03d}`），但实际应该使用学生的学号（`username`）作为考号。

**正确逻辑**:
1. **学号 = 考号**: `users.username` 就是学生的考号
2. **考号映射**: 应该在 `exam_number_mappings` 表中建立考试与学生的考号映射关系
3. **考号连续性**: 不再重要，重要的是使用学生自己的学号

---

## ✅ 修复内容

### 1. 修改 `_assign_by_class` 函数

**文件**: `backend/app/services/exam_room_service.py`

**修改前**:
```python
# 生成考号：{year}{room_idx:02d}{seat:03d}
room_idx = room_index + 1
exam_number = f"{year}{room_idx:02d}{current_seat:03d}"  # ❌ 错误的考号生成

seat = ExamRoomStudent(
    room_id=room.id,
    student_id=student.id,
    exam_number=exam_number,  # ❌ 使用生成的考号
    ...
)
db.add(seat)
# ❌ 没有创建 ExamNumberMapping
```

**修改后**:
```python
# 使用 username 作为考号（学号 = 考号）
exam_number = student.username  # ✅ 使用学号作为考号

# 创建座位分配
seat = ExamRoomStudent(
    room_id=room.id,
    student_id=student.id,
    exam_number=exam_number,  # ✅ 使用学号作为考号
    seat_number=current_seat,
    student_id_number=student.student_id_number,
    student_name=student.full_name,
    school_id=student.school_id,
    classroom_id=student.classroom_id,
)
db.add(seat)

# 创建考号映射
mapping = ExamNumberMapping(
    exam_id=exam_id,
    student_id=student.id,
    exam_number=exam_number,  # ✅ 使用学号作为考号
    student_id_number=student.student_id_number,
    school_id=student.school_id,
    classroom_id=student.classroom_id,
)
db.add(mapping)  # ✅ 创建考号映射记录
```

### 2. 修改 `_assign_mixed` 函数

**修改后**:
```python
# 使用 username 作为考号（学号 = 考号）
exam_number = student.username  # ✅ 使用学号

seat = ExamRoomStudent(
    room_id=room.id,
    student_id=student.id,
    exam_number=exam_number,  # ✅ 使用学号
    ...
)
db.add(seat)

# 创建考号映射
mapping = ExamNumberMapping(
    exam_id=exam_id,
    student_id=student.id,
    exam_number=exam_number,  # ✅ 使用学号
    ...
)
db.add(mapping)  # ✅ 创建考号映射
```

### 3. 更新考号范围逻辑

**修改前**:
```python
room.exam_number_start = f"{year}{idx:02d}001"  # ❌ 固定格式
room.exam_number_end = f"{year}{idx:02d}{seat_count:03d}"  # ❌ 固定格式
```

**修改后**:
```python
# 获取该考场的考号范围
numbers_result = await db.execute(
    select(ExamRoomStudent.exam_number)
    .where(ExamRoomStudent.room_id == room.id)
    .order_by(ExamRoomStudent.seat_number)
)
numbers = [n[0] for n in numbers_result.all()]
if numbers:
    room.exam_number_start = numbers[0]  # ✅ 第一个学生的学号
    room.exam_number_end = numbers[-1]  # ✅ 最后一个学生的学号
```

### 4. 传递 exam_id 参数

**修改函数签名**:
```python
async def _assign_students_to_rooms(
    self,
    exam_rooms: List[ExamRoom],
    students: List[User],
    request: AutoAssignRoomsRequest,
    db: AsyncSession,
    exam_id: int,  # ✅ 添加 exam_id 参数
):
```

---

## 📊 数据库表结构

### `users` 表（学生账户）

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,  -- 学号 = 考号 ✅
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL,  -- 'student'
    student_id_number VARCHAR(50) UNIQUE,  -- 学籍号
    school_id INTEGER,
    grade_id INTEGER,
    classroom_id INTEGER,
    ...
);
```

**关键**:
- `username` = 学号 = 考号
- `student_id_number` = 学籍号（身份证号等）

### `exam_number_mappings` 表（考号映射）

```sql
CREATE TABLE exam_number_mappings (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    exam_number VARCHAR(50) NOT NULL,  -- 考号 = username ✅
    student_id_number VARCHAR(50) NOT NULL,
    school_id INTEGER NOT NULL,
    classroom_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (school_id) REFERENCES schools(id),
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id),
    UNIQUE(exam_id, exam_number)  -- 同一考试中考号唯一
);
```

**用途**:
- 记录某次考试中，学生的考号
- 支持跨学年追踪学生的考试表现
- 考号 = 学号，便于识别

### `exam_room_students` 表（考场学生）

```sql
CREATE TABLE exam_room_students (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    exam_number VARCHAR(20) NOT NULL,  -- 考号 = username ✅
    seat_number INTEGER NOT NULL,
    student_id_number VARCHAR(50),
    student_name VARCHAR(100),
    school_id INTEGER,
    classroom_id INTEGER,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (room_id) REFERENCES exam_rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id),
    UNIQUE(room_id, exam_number),  -- 同一考场中考号唯一
    UNIQUE(room_id, seat_number)  -- 同一考场中座位号唯一
);
```

**用途**:
- 记录学生在某考场的座位分配
- 使用学号作为考号

---

## 🔄 数据流程

### 修复前（错误）

```
学生数据 (users表)
    ↓ username = "2024100001"
    ↓ student_id_number = "123456789012345678"

考场分配
    ↓
生成考号 = "202601001"  ❌ 无意义
    ↓
exam_room_students.exam_number = "202601001"  ❌
    ↓
没有创建 exam_number_mappings 记录  ❌
```

### 修复后（正确）

```
学生数据 (users表)
    ↓ username = "2024100001"  ← 这是学号，也是考号 ✅
    ↓ student_id_number = "123456789012345678"

考场分配
    ↓
使用学号作为考号 = "2024100001"  ✅
    ↓
exam_room_students.exam_number = "2024100001"  ✅
    ↓
创建 exam_number_mappings 记录  ✅
    ├─ exam_id = 1
    ├─ student_id = 243
    ├─ exam_number = "2024100001"  ← 学号 ✅
    ├─ student_id_number = "123456789012345678"
    ├─ school_id = 126
    └─ classroom_id = 73
```

---

## 💡 设计优势

### 1. 直观性

**修复前**:
- 考号: `202601001` - 无法识别学生
- 需要查询对应表才知道是谁

**修复后**:
- 考号: `2024100001` - 直接知道是哪个学生
- 无需查询，一目了然

### 2. 跨考试追踪

```sql
-- 查询学生在多次考试中的表现
SELECT
    e.name AS exam_name,
    e.exam_date,
    erm.exam_number,
    u.full_name,
    ers.room_id,
    ers.seat_number
FROM exam_number_mappings erm
JOIN exams e ON erm.exam_id = e.id
JOIN users u ON erm.student_id = u.id
LEFT JOIN exam_room_students ers ON ers.exam_number = erm.exam_number
WHERE u.username = '2024100001'
ORDER BY e.exam_date;
```

**结果**:
```
| 考试名称 | 考试日期 | 考号 | 姓名 | 考场 | 座位 |
|---------|---------|----------|------|------|------|
| 期中考试 | 2026-01-15 | 2024100001 | 张三 | 1 | 15 |
| 期末考试 | 2026-06-20 | 2024100001 | 张三 | 3 | 08 |
```

### 3. 唯一性保证

- ✅ `username` 在 `users` 表中唯一
- ✅ `exam_number` 在 `exam_number_mappings` 表中（按考试）唯一
- ✅ `exam_number` 在 `exam_room_students` 表中（按考场）唯一

### 4. 简化逻辑

**修复前**:
- 需要生成考号
- 需要维护考号规则
- 需要考号对应关系

**修复后**:
- 直接使用学号
- 无需额外规则
- 对应关系清晰

---

## 📋 示例数据

### users 表（学生）

```
| id  | username    | full_name | student_id_number       | school_id | classroom_id |
|-----|-------------|-----------|-------------------------|-----------|--------------|
| 243 | 2024100001  | 张三      | 440804201111111814     | 126       | 73           |
| 244 | 2024100002  | 李四      | 440783201201076610     | 126       | 73           |
| 245 | 2024100003  | 王五      | 440783201205032711     | 126       | 73           |
```

### exam_number_mappings 表（考号映射）

```
| id | exam_id | student_id | exam_number  | student_id_number       | school_id | classroom_id |
|----|---------|------------|--------------|-------------------------|-----------|--------------|
| 1  | 1       | 243        | 2024100001   | 440804201111111814     | 126       | 73           |
| 2  | 1       | 244        | 2024100002   | 440783201201076610     | 126       | 73           |
| 3  | 1       | 245        | 2024100003   | 440783201205032711     | 126       | 73           |
```

### exam_room_students 表（考场学生）

```
| id | room_id | student_id | exam_number  | seat_number | student_name | school_id | classroom_id |
|----|---------|------------|--------------|-------------|--------------|-----------|--------------|
| 1  | 1       | 243        | 2024100001   | 1           | 张三         | 126       | 73           |
| 2  | 1       | 244        | 2024100002   | 2           | 李四         | 126       | 73           |
| 3  | 1       | 245        | 2024100003   | 3           | 王五         | 126       | 73           |
```

### exam_rooms 表（考场）

```
| id | exam_id | name       | seat_count | exam_number_start | exam_number_end |
|----|---------|------------|------------|-------------------|-----------------|
| 1  | 1       | 第1考场    | 30         | 2024100001       | 2024100030     |
| 2  | 1       | 第2考场    | 30         | 2024100031       | 2024100060     |
```

---

## ✅ 验证清单

- [x] 使用 `username` 作为考号
- [x] 在 `exam_number_mappings` 表中创建映射记录
- [x] 更新 `_assign_by_class` 函数
- [x] 更新 `_assign_mixed` 函数
- [x] 更新考号范围逻辑（使用实际的学号）
- [x] 传递 `exam_id` 参数
- [x] Python 代码格式化（black）

---

## 🎉 修复完成

✅ **考号使用学号**: `exam_number = student.username`
✅ **创建考号映射**: 在 `exam_number_mappings` 表中记录
✅ **更新考号范围**: 使用实际的学号范围
✅ **简化逻辑**: 无需生成复杂考号

**现在考场分配使用学号作为考号了！** 🚀

---

## 📚 相关文档

- [考场分配Session绑定错误修复](exam-room-session-binding-fix.md)
- [考场分配考号缺失错误修复](exam-room-assignment-exam-number-fix.md)
- [学生导入字段不匹配错误修复](student-import-field-mismatch-fix.md)

---

**修复时间**: 2026-01-17
**修改**: 考号从自动生成改为使用学号
**原因**: 学号就是考号，更直观合理
**状态**: ✅ 已修复
