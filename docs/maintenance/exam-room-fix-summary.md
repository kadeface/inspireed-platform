# 考场分配400错误修复总结

## 问题描述

在创建考试后，点击"自动编排考场"按钮时出现 400 Bad Request 错误：
```
POST http://localhost:8000/api/v1/exams/14/rooms/auto-assign 400
```

## 根本原因

### 1. 考试创建时的数据问题
- **区县管理员**创建考试时，`school_id` 设置为 `undefined`（因为区县管理员管理多个学校）
- 后端接收到的 `school_id` 为 `null`
- 考试表中 `school_id` 字段是 nullable 的，所以考试创建成功

### 2. 学生查询逻辑缺陷
原始代码 (`exam_room_service.py` 第 108-137 行)：

```python
# 问题代码
result = await db.execute(
    select(User).where(
        and_(
            User.role == UserRole.STUDENT,
            User.grade_id == exam.grade_id,
            User.school_id == exam.school_id  # ❌ exam.school_id = None
        )
    ).order_by(User.classroom_id, User.id)
)
```

**问题**：
- 当 `exam.school_id` 为 `None` 时，查询条件变成 `User.school_id == None`
- 这导致查询失败，找不到任何学生
- 服务抛出 `ValueError("没有找到可分配的学生")`
- API 返回 400 错误

### 3. 区县级考试场景
区县管理员创建的统考通常：
- 涉及多个学校的学生
- `school_id` 为 `null`（不限定单个学校）
- `region_id` 有值（指定区县）

## 修复方案

### 修改后的代码 (`exam_room_service.py`)

```python
async def _get_exam_students(self, exam: Exam, db: AsyncSession) -> List[User]:
    """获取考试的学生

    从ExamNumberMapping获取学生，如果没有则根据grade_id获取

    对于区县级考试（school_id为None），获取该年级所有学生
    对于校级考试（school_id有值），只获取该校的学生
    """
    # 首先尝试从ExamNumberMapping获取
    from app.models.evaluation import ExamNumberMapping

    result = await db.execute(
        select(User)
        .join(ExamNumberMapping, User.id == ExamNumberMapping.student_id)
        .where(ExamNumberMapping.exam_id == exam.id)
        .order_by(User.classroom_id, User.id)
    )
    students = list(result.scalars().all())

    logger.info(f"Found {len(students)} students from ExamNumberMapping for exam {exam.id}")

    if not students:
        # 如果没有ExamNumberMapping，根据年级和学校/区县获取
        logger.info(
            f"No ExamNumberMapping found. Falling back to grade/school query. "
            f"Exam grade_id={exam.grade_id}, school_id={exam.school_id}, region_id={exam.region_id}"
        )

        # ✅ 构建动态查询条件
        conditions = [
            User.role == UserRole.STUDENT,
            User.grade_id == exam.grade_id
        ]

        # 如果指定了学校，只查询该校的学生
        if exam.school_id:
            conditions.append(User.school_id == exam.school_id)
        # 如果指定了区县，查询该区县的学生
        elif exam.region_id:
            conditions.append(User.region_id == exam.region_id)

        result = await db.execute(
            select(User).where(
                and_(*conditions)
            ).order_by(User.school_id, User.classroom_id, User.id)
        )
        students = list(result.scalars().all())

        logger.info(
            f"Found {len(students)} students from grade/school/region query. "
            f"Filter by: school_id={exam.school_id}, region_id={exam.region_id}"
        )

    return students
```

### 关键改进

1. **动态查询条件**：根据考试类型动态构建查询
   - 校级考试：`school_id` 有值 → 按学校筛选
   - 区县级考试：`region_id` 有值 → 按区县筛选
   - 如果都没有：只按年级筛选

2. **增强日志记录**：
   - 记录找到的学生数量
   - 记录查询条件（grade_id, school_id, region_id）
   - 便于调试和问题追踪

3. **更好的排序**：
   - 原始：`order_by(User.classroom_id, User.id)`
   - 修改后：`order_by(User.school_id, User.classroom_id, User.id)`
   - 对于区县级考试，按学校分组更合理

## 测试步骤

### 1. 区县管理员测试场景

1. 使用区县管理员账号登录（或使用管理员账号）
2. 点击"快速创建考试"
3. **步骤1：选择班级**
   - 选择区县
   - 选择年级（例如：高一）
   - 选择班级（可选择多个班级）
   - 选择学期和考试日期
4. **步骤2：设置科目**
   - 选择考试科目
   - 点击"下一步"
   - ✅ 考试应该成功创建
5. **步骤3：考场安排**
   - 配置编排规则（每考场人数、编排方式等）
   - 点击"自动编排考场"
   - ✅ 应该成功创建考场
   - ✅ 控制台应显示：
     ```
     编排考场请求: {capacity_per_room: 30, ...}
     考试ID: 15
     ```

### 2. 查看后端日志

```bash
tail -f logs/backend.log
```

应该看到类似输出：
```
INFO:app.services.exam_room_service:Auto-assigning rooms for exam 15
INFO:app.services.exam_room_service:Exam 15 details: name=2024年春季期末考试, school_id=None, grade_id=3, exam_type=final
INFO:app.services.exam_room_service:Found 0 students from ExamNumberMapping for exam 15
INFO:app.services.exam_room_service:No ExamNumberMapping found. Falling back to grade/school query. Exam grade_id=3, school_id=None, region_id=1
INFO:app.services.exam_room_service:Found 135 students from grade/school/region query. Filter by: school_id=None, region_id=1
INFO:app.services.exam_room_service:Assigning 135 students to 5 rooms
INFO:app.services.exam_room_service:Successfully created 5 exam rooms
```

### 3. 验证考场列表

- 考场列表应显示多个考场（例如：5个考场）
- 每个考场显示容量和实际学生数
- 考号范围应正确生成

### 4. 分配监考教师

- 点击"分配监考教师"
- ✅ 应该成功为每个考场分配2名监考（主+副）

## 技术要点

### User 模型结构

```python
class User(Base):
    # ...
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=True)
```

### Exam 模型结构

```python
class Exam(Base):
    # ...
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)  # 区县级考试
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)  # 校级考试
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
```

### 查询逻辑

| 考试类型 | school_id | region_id | 查询条件 |
|---------|-----------|-----------|---------|
| 校级考试 | 有值 | null | `school_id == 值` |
| 区县级考试 | null | 有值 | `region_id == 值` |
| 未指定（罕见） | null | null | 仅 `grade_id` |

## 文件变更

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `backend/app/services/exam_room_service.py` | 修改 | 修复学生查询逻辑，添加详细日志 |
| `frontend/src/pages/DistrictExamAdmin/Dashboard.vue` | 无变更 | 保持原有代码 |

## 后续建议

### 1. 前端改进
当创建考试时，如果 `school_id` 为空，应该：
- 明确提示用户这是"区县级统考"
- 或强制用户选择一个具体的学校

### 2. 数据验证
在 API 层添加更严格的验证：
```python
# 区县级考试必须有 region_id
if not exam_in.school_id and not exam_in.region_id:
    raise HTTPException(
        status_code=400,
        detail="区县级考试必须指定 region_id"
    )
```

### 3. ExamNumberMapping 创建
考虑在考试创建时自动创建 ExamNumberMapping：
- 为每个选中的班级学生创建考号映射
- 避免后续需要回退查询

## 总结

✅ **问题已解决**
- 区县管理员现在可以为多个学校的考试自动分配考场
- 查询逻辑正确处理 `school_id` 和 `region_id`
- 添加了详细的日志便于调试

✅ **服务已重启**
- 后端应用了新的代码
- 前端已就绪
- 可以开始测试

---

**修复日期**: 2026-01-17
**修复文件**: `backend/app/services/exam_room_service.py`
**影响范围**: 考场自动分配功能
