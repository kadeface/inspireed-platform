# StudentType 使用说明

## 概述

`StudentType` 是用于标识学生文理科分类的枚举类型，支持不同学段和不同分科阶段的灵活配置。

## 枚举值

| 值 | 说明 | 适用场景 |
|---|---|---|
| `none` | 未分科 | 小学生、初中生、高中未分科阶段（如高一第一学期） |
| `arts` | 文科 | 高中文科方向（历史方向/偏文） |
| `science` | 理科 | 高中理科方向（物理方向/偏理） |

## 使用场景

### 1. 义务教育阶段（小学、初中）

```python
# 小学生和初中生通常不分科
student = User(
    full_name="张三",
    grade_id=primary_school_grade_id,  # 小学
    student_type=StudentType.NONE
)
```

### 2. 高中未分科阶段

```python
# 高一第一学期，或选科前的学生
student = User(
    full_name="李四",
    grade_id=grade_10_id,  # 高一
    student_type=StudentType.NONE  # 尚未分科
)
```

### 3. 高中已分科阶段

```python
# 高二、高三已分科的学生
arts_student = User(
    full_name="王五",
    grade_id=grade_11_id,  # 高二
    student_type=StudentType.ARTS  # 文科
)

science_student = User(
    full_name="赵六",
    grade_id=grade_11_id,  # 高二
    student_type=StudentType.SCIENCE  # 理科
)
```

## 注意事项

### 分科时间因地区和学校而异

不同地区、不同学校的分科时间可能不同：

- **传统模式**：高二开始分科
- **新高考模式**：
  - "3+1+2"模式：高一结束后选科
  - "3+3"模式：高一第二学期选科
  - 部分学校：高一第一学期结束就选科

**建议**：由学校管理员根据实际情况在系统中设置学生的 `student_type`。

### 分科不是强制的

- 部分学生可能始终不分科（如综合素质评价）
- 某些特殊班级可能不分科
- 这些学生的 `student_type` 应保持为 `NONE`

### 总分评价的使用

`ExamTotalScore` 模型主要用于高中总分评价（如高考、模考）：

```python
# 理科学生高考总分
total_score = ExamTotalScore(
    exam_id=gaoke_exam_id,
    student_id=science_student.id,
    student_type=StudentType.SCIENCE,
    total_score=680,
    c9_line=670,           # 理科C9线
    special_control_line=620,  # 理科特控线
    undergraduate_line=520,    # 理科本科线
    junior_college_line=200,   # 专科线（文理相同）
    reached_c9=True,           # 自动计算达标情况
    reached_special_control=True,
    reached_undergraduate=True,
    reached_junior_college=True
)
```

## 数据模型关系

```
User
├── student_type: StudentType (用户级别)
│
└── ExamTotalScore
    └── student_type: StudentType (冗余存储，便于查询)
```

## API 示例

### 获取学生列表（按文理科筛选）

```python
# 获取所有理科学生
science_students = await session.execute(
    select(User).where(User.student_type == StudentType.SCIENCE)
)

# 获取未分科的学生
none_type_students = await session.execute(
    select(User).where(User.student_type == StudentType.NONE)
)
```

### 更新学生类型

```python
# 学生分科后更新类型
student = await session.get(User, student_id)
student.student_type = StudentType.ARTS
await session.commit()
```

### 统计各科类学生人数

```python
from sqlalchemy import func

# 统计各类学生人数
result = await session.execute(
    select(User.student_type, func.count(User.id))
    .group_by(User.student_type)
)

# 结果示例：
# none: 1500 (小学+初中+高一未分科)
# arts: 300 (文科生)
# science: 500 (理科生)
```

## 常见问题

### Q: 高一学生什么时候设置 student_type？

A: 取决于学校的选科时间。通常在选科确定后将 student_type 从 NONE 改为 ARTS 或 SCIENCE。

### Q: 如果学生中途转科怎么办？

A: 更新学生的 student_type 即可。但需要注意：
- 历史成绩记录保持不变
- 新的成绩使用新的 student_type
- 建议记录转科时间和原因

### Q: 小学生需要设置 student_type 吗？

A: 不是必须的。如果未设置，默认值为 NONE。但建议在用户创建时明确设置，保持数据一致性。

### Q: ExamTotalScore 中 student_type 字段的作用？

A:
1. 冗余存储：避免每次查询都要关联 User 表
2. 历史记录：即使 User.student_type 变更，历史总分记录的 student_type 保持不变
3. 性能优化：按文理科统计时不需要 JOIN User 表

## 最佳实践

1. **在学生入学时设置 student_type**
   - 小学、初中：设置为 NONE
   - 高一：设置为 NONE（待分科）

2. **在选科确定后及时更新**
   - 学校管理员应在选科后批量更新
   - 建议提供批量导入功能

3. **保持 User 和 ExamTotalScore 的一致性**
   - 创建 ExamTotalScore 时从 User.student_type 复制
   - 不自动同步，允许历史记录保持原值

4. **数据校验**
   - 创建 ExamTotalScore 时检查 User.student_type 是否已设置
   - 对于已分科学生（ARTS/SCIENCE），确保使用对应科目的分数线

## 参考资料

- 新高考"3+1+2"模式解读
- 各省市高考改革方案
- 学生生涯规划指导
