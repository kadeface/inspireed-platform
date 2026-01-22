# 学生标识符与追踪机制设计文档

**日期：** 2025-01-22
**版本：** 1.0
**作者：** Claude & 用户
**状态：** 设计阶段

---

## 1. 概述

### 1.1 背景

InspireEd平台当前存在数据冗余和跨校追踪不完善的问题：
- 班级编码（如"701"）包含年级信息，与`grade_id`重复
- 用户名格式不统一，缺少规范
- 考号生成策略单一，跨校学生追踪困难

### 1.2 设计目标

1. **消除数据冗余**：优化班级编码格式，去除重复信息
2. **标准化用户名**：建立统一的用户名生成规则
3. **支持跨校追踪**：基于身份证号实现学生长期追踪
4. **增强增值分析**：支持跨年级、跨学校的成绩增长分析

### 1.3 核心原则

**以身份证号为永久追踪主线，用户名和考号作为场景化标识符**

---

## 2. 三大标识符设计

### 2.1 标识符职责划分

| 标识符 | 格式 | 长度 | 用途 | 不变性 |
|--------|------|------|------|--------|
| **身份证号** | 18位标准 | 18位 | 永久追踪标识 | 永远不变 ⭐ |
| **用户名** | 学校编码+身份证后6位 | 10位 | 登录凭证 | 同校不变，转学更新 |
| **考号** | 学校编码+入学年份+班级号+座位号 | 12位 | 考试标识 | 每次考试可能不同 |

### 2.2 身份证号（student_id_number）

**格式：** 18位国家标准身份证号

**用途：**
- 学生永久唯一标识
- 跨校、跨年级追踪的主键
- 成绩关联的主要标识

**存储位置：**
- `users.student_id_number`（主表）
- `scores.student_id_number`（冗余，保证数据可追溯）
- `exam_number_mappings.student_id_number`（冗余）

**示例：** `110101200501011234`

### 2.3 用户名（username）

**格式：** `学校编码(4位) + 身份证后6位`

**生成规则：**
```python
username = f"{school_code}{student_id_number[-6:]}"
示例：4401 + 011234 = 4401011234
```

**冲突处理：**
- 重复概率：约0.0001%（极低）
- 处理策略：添加字母后缀（A, B, C...）

**示例：**
```
学生A：110101200501011234 → 4401011234
学生B：110101200501019999 → 4401999999
学生C：身份证后6位也是011234 → 4401011234A（冲突）
```

**不变性：**
- 同一学校内：保持不变
- 转学后：更新为新学校的用户名
- 通过身份证号关联历史数据

### 2.4 考号（exam_number）

**格式：** `学校编码(4位) + 入学年份(4位) + 班序号(2位) + 座位号(2位)`

**生成规则：**
```python
exam_number = f"{school_code}{enrollment_year}{class_sequence}{seat_number:02d}"
示例：4401 + 2023 + 01 + 01 = 440120230101
```

**支持两种模式：**
1. **系统自动生成**：按规则自动生成
2. **用户自定义导入**：Excel导入时手动指定

**示例场景：**
- 2023年期中考试：440120230101
- 2023年期末考试：440120230101（同一学年稳定）
- 2024年期中考试：440120230101（升年级仍稳定）

---

## 3. 班级编码优化

### 3.1 当前问题

```
当前设计：
classroom.code = "701"  # 7年级01班
classroom.grade_id = 7  # 年级ID
classroom.enrollment_year = 2023  # 入学年份

问题：code中的"7"与grade_id重复
```

### 3.2 优化方案

**新格式：** `入学年份后2位 + 班序号(2位)`

```
优化后：
classroom.code = "2301"  # 2023年入学01班
classroom.grade_id = 7   # 当前年级（动态）
classroom.enrollment_year = 2023

优势：
✓ 消除与grade_id的冗余
✓ 升年级后编码稳定（2301永远是2301班）
✓ 包含完整的学生cohort信息
```

### 3.3 班级编码示例

| 旧编码 | 新编码 | 入学年份 | 2023年 | 2024年 | 2025年 |
|--------|--------|---------|--------|--------|--------|
| 101 | 1901 | 2019 | 4年级 | 5年级 | 6年级 |
| 701 | 2301 | 2023 | 7年级 | 8年级 | 9年级 |
| 1001 | 2301 | 2023 | 10年级 | 11年级 | 12年级 |

---

## 4. 数据库变更

### 4.1 Classroom表（班级表）

**变更：**
```python
class Classroom(Base):
    # 原有字段
    name = Column(String(100), comment="班级名称")
    code = Column(String(50), comment="班级编码")  # 格式变更：701 → 2301
    grade_id = Column(Integer, ForeignKey("grades.id"))
    enrollment_year = Column(Integer, comment="入学年份")  # 已存在

    # 新增字段：无
```

**迁移逻辑：**
```python
# 从 "701" 改为 "2301"
year_suffix = str(classroom.enrollment_year)[-2:]  # "23"
class_seq = old_code[-2:].zfill(2)                 # "01"
new_code = f"{year_suffix}{class_seq}"             # "2301"
```

### 4.2 User表（用户表）

**新增字段：**
```python
class User(Base):
    username = Column(String(20), unique=True, nullable=False)  # 格式变更
    student_id_number = Column(String(50), unique=True, index=True)  # 已存在

    # 新增
    seat_number = Column(Integer, nullable=True, comment="座位号")
```

**用户名生成：**
```python
def generate_username(school_code: str, student_id_number: str) -> str:
    base = f"{school_code}{student_id_number[-6:]}"

    # 检查冲突
    if exists(base):
        # 添加后缀：A, B, C...
        return f"{base}A"

    return base
```

**座位号规范：**
- 存储：Integer类型（1, 2, 3...）
- 显示：2位格式（01, 02, 03...）
- 分配：按班级学生顺序自动分配

### 4.3 约束和索引

**新增约束：**
```sql
-- 用户名唯一性（已存在，保持）
ALTER TABLE users ADD CONSTRAINT uq_username UNIQUE (username);

-- 座位号+班级唯一性（可选）
ALTER TABLE users ADD CONSTRAINT uq_classroom_seat
  UNIQUE (classroom_id, seat_number);
```

**新增索引：**
```sql
-- 优化增值分析查询（已存在）
CREATE INDEX idx_scores_student_id_number ON scores(student_id_number);
CREATE INDEX idx_scores_exam_student_number ON scores(exam_id, student_id_number);
```

---

## 5. 数据迁移策略

### 5.1 迁移范围

1. **classrooms.code** - 从"701"改为"2301"
2. **users.username** - 按新规则重生成
3. **users.seat_number** - 初始化为班级内序号

### 5.2 迁移步骤

**第一步：备份**
```python
def backup_before_migration():
    """迁移前备份关键表"""
    # 导出到JSON/CSV
    # 或创建数据库快照
    pass
```

**第二步：班级编码迁移**
```python
def migrate_classroom_codes(db: Session):
    for classroom in db.query(Classroom).all():
        year_suffix = str(classroom.enrollment_year)[-2:]
        class_seq = str(classroom.code)[-2:].zfill(2)
        classroom.code = f"{year_suffix}{class_seq}"
        db.add(classroom)
    db.commit()
```

**第三步：用户名迁移**
```python
def migrate_usernames(db: Session):
    for school in db.query(School).all():
        students = db.query(User).filter(
            User.school_id == school.id,
            User.role == UserRole.STUDENT
        ).all()

        username_counts = {}
        for student in students:
            base = f"{school.code}{student.student_id_number[-6:]}"
            count = username_counts.get(base, 0)

            if count == 0:
                new_username = base
            else:
                new_username = f"{base}{chr(65 + count)}"  # A, B, C...

            student.username = new_username
            username_counts[base] = count + 1
            db.add(student)

    db.commit()
```

**第四步：座位号初始化**
```python
def initialize_seat_numbers(db: Session):
    for classroom in db.query(Classroom).all():
        students = db.query(User).filter(
            User.classroom_id == classroom.id
        ).order_by(User.id).all()

        for idx, student in enumerate(students, start=1):
            student.seat_number = idx
            db.add(student)

    db.commit()
```

**第五步：验证**
```python
def validate_migration(db: Session) -> bool:
    # 检查用户名唯一性
    duplicates = db.execute("""
        SELECT username, COUNT(*) FROM users
        GROUP BY username HAVING COUNT(*) > 1
    """).fetchall()

    if duplicates:
        print(f"❌ 发现重复用户名: {duplicates}")
        return False

    # 检查班级编码格式
    invalid = db.execute("""
        SELECT code FROM classrooms
        WHERE code !~ '^\d{4}$'
    """).fetchall()

    if invalid:
        print(f"❌ 班级编码格式错误: {invalid}")
        return False

    print("✅ 迁移验证通过")
    return True
```

### 5.3 回滚机制

```python
def rollback_migration():
    """恢复备份数据"""
    # 从备份恢复classrooms.code
    # 从备份恢复users.username
    pass
```

---

## 6. 成绩关联与增值分析

### 6.1 核心设计：双键关联

**Score表结构（已存在）：**
```python
class Score(Base):
    # 双键设计
    student_id = Column(Integer, ForeignKey("users.id"))        # 临时关联
    student_id_number = Column(String(50))                       # 永久关联 ⭐

    # 成绩数据
    raw_score = Column(Integer)
    standard_score = Column(Float)
    percentile = Column(Float)
```

**设计优势：**
- `student_id`：快速关联当前用户记录
- `student_id_number`：永久追踪，跨校分析 ⭐

### 6.2 跨校追踪查询

**场景：学生转学后的成绩追踪**

```python
def get_student_growth_analysis(
    db: Session,
    student_id_number: str,
    subject_id: Optional[int] = None
):
    """
    基于身份证号查询历史成绩（增值分析）
    """
    query = db.query(Score).join(Exam).join(User).filter(
        Score.student_id_number == student_id_number
    )

    if subject_id:
        query = query.filter(Score.subject_id == subject_id)

    scores = query.order_by(Exam.exam_date).all()

    # 计算增值
    growth_data = []
    for i, score in enumerate(scores):
        growth = None
        if i > 0:
            growth = score.raw_score - scores[i-1].raw_score

        growth_data.append({
            "exam_name": score.exam.name,
            "exam_date": score.exam.exam_date,
            "raw_score": score.raw_score,
            "school": score.student.school.name,  # 显示转学信息
            "growth": growth
        })

    return growth_data
```

**示例输出：**
```json
[
  {
    "exam_name": "2023年期中考试",
    "exam_date": "2023-11-15",
    "raw_score": 85,
    "school": "四十四中",
    "growth": null
  },
  {
    "exam_name": "2024年期末考试",
    "exam_date": "2024-01-20",
    "raw_score": 90,
    "school": "五十五中",  // 转学了
    "growth": 5  // 增值+5分 ⭐
  }
]
```

### 6.3 批量增值分析

**API端点：**
```
POST /api/v1/admin/analytics/value-added-report
```

**请求参数：**
```json
{
  "exam_start_id": 1,
  "exam_end_id": 2,
  "school_id": 1,
  "grade_id": 7,
  "subject_id": 1
}
```

**返回数据：**
```json
{
  "summary": {
    "total_students": 300,
    "avg_growth": 5.2,
    "positive_growth": 240,
    "negative_growth": 60
  },
  "students": [
    {
      "student_id_number": "110101200501011234",
      "student_name": "张三",
      "current_school": "四十四中",
      "scores": [
        {"exam_id": 1, "score": 85},
        {"exam_id": 2, "score": 90}
      ],
      "total_growth": 5
    }
  ]
}
```

### 6.4 考号关联查询

```python
def get_scores_by_exam_number(
    db: Session,
    exam_id: int,
    exam_number: str
):
    """
    通过考号查询学生成绩
    """
    # 1. 通过考号找到身份证号
    mapping = db.query(ExamNumberMapping).filter(
        ExamNumberMapping.exam_id == exam_id,
        ExamNumberMapping.exam_number == exam_number
    ).first()

    # 2. 使用身份证号查询所有成绩 ⭐
    scores = db.query(Score).filter(
        Score.student_id_number == mapping.student_id_number
    ).all()

    return scores
```

---

## 7. 导入流程更新

### 7.1 学生导入逻辑

**新的Excel模板：**

| 学校名称 | 年级级别 | 班级编号 | 身份证号 | 姓名 | 座位号（可选）|
|---------|---------|---------|---------|------|-------------|
| 四十四中 | 7 | 01班 | 110101... | 张三 | 01 |
| 四十四中 | 7 | 02班 | 110101... | 李四 | 02 |

**处理流程：**
```python
async def process_student_import(record: dict, db: AsyncSession):
    # 1. 查找或创建班级（自动转换编码格式）
    classroom = await find_or_create_classroom(
        db, school_name, grade_level, classroom_code_raw
    )

    # 2. 生成用户名（新规则）
    username = generate_username(
        db, school.code, student_id_number
    )

    # 3. 检查学生是否存在（基于身份证号）
    existing = await db.query(User).filter(
        User.student_id_number == student_id_number
    ).first()

    if existing:
        # 更新班级和用户名
        existing.classroom_id = classroom.id
        existing.username = username
        return {"status": "updated"}

    # 4. 创建新学生
    student = User(
        username=username,
        student_id_number=student_id_number,
        classroom_id=classroom.id,
        seat_number=seat_number
    )
    db.add(student)

    return {"status": "created"}
```

### 7.2 考号导入逻辑

**Excel模板：**

| 考号（可选）| 身份证号 | 姓名 | 考试ID |
|-----------|---------|------|--------|
| 440120230101 | 110101... | 张三 | 1 |
| | 110101... | 李四 | 1 |

**处理流程：**
```python
async def process_exam_number_import(record: dict, db: AsyncSession):
    student_id_number = record["student_id_number"]
    exam_id = record["exam_id"]
    exam_number = record.get("exam_number")  # 可选

    # 查找学生
    student = await db.query(User).filter(
        User.student_id_number == student_id_number
    ).first()

    # 如果未提供考号，自动生成
    if not exam_number:
        classroom = await db.get(Classroom, student.classroom_id)
        school = await db.get(School, student.school_id)

        exam_number = f"{school.code}{classroom.enrollment_year}{classroom.code[-2:]}{student.seat_number:02d}"

    # 验证唯一性并创建映射
    mapping = ExamNumberMapping(
        exam_id=exam_id,
        exam_number=exam_number,
        student_id=student.id,
        student_id_number=student_id_number,
        school_id=student.school_id,
        classroom_id=student.classroom_id
    )
    db.add(mapping)

    return {"status": "created", "exam_number": exam_number}
```

---

## 8. API端点设计

### 8.1 新增API端点

**1. 用户名冲突检测**
```
GET /api/v1/admin/users/check-username
参数：school_code, student_id_number
返回：{available: true, username: "4401011234"}
```

**2. 批量生成考号**
```
POST /api/v1/admin/exams/generate-exam-numbers
请求：{exam_id: 1, school_id: 1, auto_generate: true}
返回：{generated: 1200, exam_numbers: [...]}
```

**3. 学生增值分析**
```
GET /api/v1/admin/analytics/student-growth/{student_id_number}
返回：学生历史成绩和增长数据
```

**4. 批量增值分析报告**
```
POST /api/v1/admin/analytics/value-added-report
返回：班级/年级/学校的汇总统计
```

**5. 班级编码转换（迁移用）**
```
GET /api/v1/admin/classrooms/preview-code-conversion
POST /api/v1/admin/classrooms/convert-codes
```

**6. 用户名重生成（迁移用）**
```
GET /api/v1/admin/users/preview-username-regeneration
POST /api/v1/admin/users/regenerate-usernames
```

### 8.2 增强现有API

**成绩录入API**
```python
POST /api/v1/admin/exams/{exam_id}/scores
支持两种方式：
1. 通过考号：{"exam_number": "440120230101", "score": 90}
2. 通过身份证号：{"student_id_number": "110101...", "score": 90}
```

---

## 9. 前端界面变更

### 9.1 显示格式调整

**座位号显示：**
```vue
<!-- 格式化为2位 -->
<td>座位号: {{ student.seat_number?.toString().padStart(2, '0') }}</td>
```

**用户名显示：**
```vue
<!-- 显示完整用户名 -->
<td>{{ student.username }}</td>
<!-- 4401011234 或 4401011234A -->
```

### 9.2 新增管理界面

**班级编码转换工具：**
- 预览转换影响范围
- 执行转换
- 查看转换日志

**用户名重生成工具：**
- 预览用户名变更
- 批量重生成
- 处理冲突

**增值分析仪表盘：**
- 学生个人成长曲线
- 班级/年级汇总统计
- 跨校学生追踪

---

## 10. 测试策略

### 10.1 单元测试

**用户名生成测试：**
```python
def test_username_generation():
    # 正常情况
    assert generate("4401", "...011234") == "4401011234"

    # 冲突处理
    assert generate_with_conflict("4401", "...011234") == "4401011234A"

    # 极端情况（A-Z用完）
    assert generate_many_conflicts() == "44010112340"
```

**考号生成测试：**
```python
def test_exam_number_generation():
    assert generate("4401", 2023, "2301", 1) == "440120230101"
    assert generate("4401", 2023, "2301", 15) == "440120230115"
```

### 10.2 集成测试

**跨校成绩追踪测试：**
```python
def test_cross_school_tracking():
    # 创建学生A在4401学校
    student = create_student("4401", "...011234")

    # 2023年考试成绩
    create_score(student, exam_id=1, score=85)

    # 转学到5501学校
    transfer_student(student, "5501")

    # 2024年考试成绩
    create_score(student, exam_id=2, score=90)

    # 增值分析
    growth = get_growth_analysis(student.student_id_number)
    assert growth[0]["score"] == 85
    assert growth[1]["score"] == 90
    assert growth[1]["growth"] == 5
```

### 10.3 数据迁移测试

**在测试环境执行完整迁移：**
1. 准备测试数据
2. 执行迁移脚本
3. 验证数据完整性
4. 测试回滚机制

---

## 11. 实施计划

### 11.1 阶段划分

**Phase 1: 数据库迁移（高优先级）**
- 班级编码格式转换
- 用户名重生成
- 座位号初始化
- 测试验证

**Phase 2: 导入流程更新（中优先级）**
- 更新学生导入逻辑
- 更新考号导入逻辑
- 冲突检测和处理

**Phase 3: API开发（中优先级）**
- 用户名/考号生成API
- 增值分析API
- 迁移工具API

**Phase 4: 前端界面更新（低优先级）**
- 显示格式调整
- 管理工具界面
- 分析仪表盘

### 11.2 风险控制

**数据安全：**
- 迁移前强制备份
- 提供回滚机制
- 在测试环境验证

**兼容性：**
- 保持现有API兼容
- 渐进式迁移
- 提供过渡期

**性能：**
- 添加必要的索引
- 优化查询语句
- 批量操作优化

---

## 12. 总结

本设计通过三个标识符的明确职责划分，实现了：

1. **消除冗余**：班级编码不再包含年级信息
2. **标准化**：用户名和考号有统一的生成规则
3. **可追踪**：基于身份证号的跨校、跨年级追踪
4. **可扩展**：支持未来的功能扩展

核心优势是使用`student_id_number`作为永久追踪键，在所有相关表中冗余存储，确保数据可追溯性。同时通过冲突处理机制保证用户名和考号的唯一性。

---

## 附录A：关键代码示例

### A.1 用户名生成器

```python
def generate_username(
    db: Session,
    school_code: str,
    student_id_number: str
) -> str:
    """
    生成用户名：学校编码 + 身份证后6位
    冲突时添加字母后缀
    """
    base_username = f"{school_code}{student_id_number[-6:]}"

    # 检查重复
    existing = db.query(User).filter(
        User.username == base_username
    ).first()

    if not existing:
        return base_username

    # 添加后缀 A, B, C...
    suffix = 0
    while True:
        suffix += 1
        username = f"{base_username}{chr(64 + suffix)}"

        existing = db.query(User).filter(
            User.username == username
        ).first()

        if not existing:
            return username

        if suffix >= 26:
            # A-Z用完，使用数字
            username = f"{base_username}{suffix - 26}"
            return username
```

### A.2 考号生成器

```python
def generate_exam_number(
    school_code: str,
    enrollment_year: int,
    classroom_code: str,
    seat_number: int
) -> str:
    """
    生成考号：学校编码 + 入学年份 + 班序号 + 座位号
    """
    class_sequence = classroom_code[-2:]
    return f"{school_code}{enrollment_year}{class_sequence}{seat_number:02d}"
```

### A.3 增值分析查询

```python
def get_student_growth(
    db: Session,
    student_id_number: str,
    subject_id: Optional[int] = None
) -> List[Dict]:
    """
    查询学生历史成绩（增值分析）
    """
    query = db.query(Score).join(Exam).filter(
        Score.student_id_number == student_id_number
    )

    if subject_id:
        query = query.filter(Score.subject_id == subject_id)

    scores = query.order_by(Exam.exam_date).all()

    result = []
    for i, score in enumerate(scores):
        growth = None
        if i > 0:
            growth = score.raw_score - scores[i-1].raw_score

        result.append({
            "exam": score.exam.name,
            "date": score.exam.exam_date.isoformat(),
            "score": score.raw_score,
            "school": score.student.school.name,
            "growth": growth
        })

    return result
```

---

**文档结束**
