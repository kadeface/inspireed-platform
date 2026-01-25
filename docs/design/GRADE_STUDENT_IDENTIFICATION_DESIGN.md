# 学生身份识别与年级变化处理设计

## 📋 目录

1. [问题分析](#问题分析)
2. [解决方案设计](#解决方案设计)
3. [数据模型扩展](#数据模型扩展)
4. [学生身份匹配策略](#学生身份匹配策略)
5. [成绩导入中的学生识别](#成绩导入中的学生识别)
6. [历史成绩查询](#历史成绩查询)
7. [实施建议](#实施建议)

---

## 🔍 问题分析

### 问题1：年级变化

**场景**：
- 学生从一年级升到二年级，`User.grade_id` 从 1 变为 2
- 但该学生一年级时的成绩记录应该保持记录当时的年级信息
- 查询历史成绩时，需要知道成绩产生时的年级

**影响**：
- 如果成绩记录依赖 `User.grade_id`，升年级后历史成绩的年级信息会丢失
- 无法准确统计学生在某个年级的成绩
- 无法生成按年级的成绩报告

### 问题2：学号变化

**场景**：
- 学生转学、复学、留级等情况可能导致学号变化
- 外部系统（如教育局统考系统）可能使用学号导入成绩
- 如果学号变化，导入时无法匹配到正确的学生

**影响**：
- 导入成绩时无法通过学号准确匹配学生
- 可能出现重复记录或数据丢失
- 需要人工干预匹配

### 问题3：学生身份识别

**场景**：
- 导入成绩时，外部系统可能只提供学号、姓名等信息
- 需要能够准确匹配到系统中的学生
- 可能存在重名、学号重复等情况

**影响**：
- 匹配失败导致导入错误
- 匹配错误导致成绩关联到错误的学生
- 需要人工确认和干预

---

## 💡 解决方案设计

### 核心原则

1. **历史快照原则**：成绩记录应该保存产生时的快照信息（年级、班级等），不依赖当前状态
2. **学籍号优先**：**学籍号（student_registration_number）作为主要的学生身份标识**，全国唯一、永久不变
3. **稳定标识优先**：优先使用稳定的标识（学籍号 > User.id）关联学生
4. **多维度匹配**：支持多种方式识别学生（学籍号、学号、姓名+年级、身份证号等）
5. **变更追踪**：记录学号、年级等关键信息的变化历史（学籍号不需要追踪，因为不变）

### 解决方案概览

```
┌─────────────────────────────────────────────────────────┐
│                  学生身份识别体系                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. 永久标识层（最高优先级）                              │
│     └─ student_registration_number (学籍号，全国唯一，永久不变) │
│                                                          │
│  2. 系统标识层                                           │
│     └─ User.id (数据库主键，永不变化)                    │
│                                                          │
│  3. 可变标识层                                           │
│     ├─ student_number (学号，可能变化)                    │
│     ├─ grade_id (年级，会变化)                           │
│     └─ classroom_id (班级，会变化)                       │
│                                                          │
│  4. 历史记录层                                           │
│     ├─ StudentNumberHistory (学号历史)                    │
│     └─ GradeRecord (记录成绩时的年级快照)                 │
│                                                          │
│  5. 匹配策略层（按优先级）                                │
│     ├─ 学籍号匹配 (student_registration_number) - 最高优先级 │
│     ├─ 精确匹配 (student_id)                             │
│     ├─ 学号匹配 (student_number)                         │
│     ├─ 姓名+年级匹配                                     │
│     └─ 身份证号匹配 (可选)                               │
└─────────────────────────────────────────────────────────┘
```

### 学籍号的优势

1. **全国唯一性**：由教育部门统一分配，全国范围内唯一
2. **永久不变性**：一旦分配，终身不变，不受转学、升年级、复学等影响
3. **业务友好**：比数据库自增ID更有业务意义，便于外部系统对接
4. **权威性**：由教育部门统一管理，具有法律效力
5. **追溯性强**：可以跨学校、跨地区追溯学生完整学习轨迹

---

## 🗄️ 数据模型扩展

### 1. User模型扩展（增加学籍号和学号字段）

```python
class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    # ... 原有字段 ...
    
    # 学籍号（全国唯一，永久不变，学生必需）
    student_registration_number = Column(
        String(50), 
        nullable=True,  # 对于学生，应该设置为NOT NULL，但考虑历史数据，暂时可为空
        unique=True,
        index=True,
        comment="学籍号，全国唯一，永久不变，由教育部门统一分配"
    )
    
    # 学号（可能变化，但通常在同一学校内唯一）
    student_number = Column(
        String(50), 
        nullable=True, 
        index=True,
        comment="学号，可能因转学、复学等情况变化，同一学校内唯一"
    )
    
    # 身份证号（可选，用于精确匹配）
    id_card_number = Column(
        String(18), 
        nullable=True, 
        index=True,
        comment="身份证号，用于精确匹配学生身份（加密存储）"
    )
    
    # 唯一性约束
    __table_args__ = (
        # 学籍号全局唯一（已在字段定义中使用unique=True）
        # 学号在同一学校内唯一
        UniqueConstraint("school_id", "student_number", name="uq_student_number_school"),
    )
    
    @validates("student_registration_number")
    def validate_student_registration_number(self, key: str, value: Optional[str]) -> Optional[str]:
        """验证学籍号格式（如果提供）"""
        if value and self.role == UserRole.STUDENT:
            # 学籍号格式验证（根据实际格式要求调整）
            # 通常学籍号是19位数字，格式：G + 8位地区代码 + 10位顺序号
            if not re.match(r'^[A-Z]\d{18}$', value):
                raise ValueError("学籍号格式不正确")
        return value
```

**设计说明**：
- **学籍号（student_registration_number）**：
  - 对于学生角色，应该设置为必需字段（NOT NULL）
  - 全局唯一（使用`unique=True`）
  - 永久不变，不受任何情况影响
  - 作为学生身份的主要标识符
  
- **学号（student_number）**：
  - 学校内部使用的学号，可能变化
  - 在同一学校内唯一
  - 用于学校内部管理和导入成绩时的辅助匹配

### 2. StudentNumberHistory模型（学号历史记录）

```python
class StudentNumberHistory(Base):
    """学号历史记录模型"""
    
    __tablename__ = "student_number_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 学生信息
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 学号信息
    student_number = Column(String(50), nullable=False, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True, index=True)
    
    # 有效期
    valid_from = Column(DateTime, nullable=False, index=True, comment="学号生效时间")
    valid_to = Column(DateTime, nullable=True, index=True, comment="学号失效时间（NULL表示当前有效）")
    
    # 变更原因
    change_reason = Column(String(200), nullable=True, comment="变更原因：转学、复学、留级等")
    
    # 操作信息
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关联关系
    student = relationship("User", foreign_keys=[student_id])
    school = relationship("School")
    changer = relationship("User", foreign_keys=[changed_by])
    
    __table_args__ = (
        Index("idx_student_number_history", "student_number", "school_id", "valid_from"),
    )
```

### 3. GradeRecord模型扩展（记录年级快照）

```python
class GradeRecord(Base):
    """成绩记录模型"""
    
    __tablename__ = "grade_records"
    
    # ... 原有字段 ...
    
    # 学生信息（使用稳定的student_id）
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 成绩产生时的快照信息（不依赖User的当前状态）
    student_registration_number = Column(
        String(50), 
        nullable=True, 
        index=True,
        comment="学籍号（全国唯一，永久不变，用于精确关联学生）"
    )
    student_grade_id_at_time = Column(
        Integer, 
        ForeignKey("grades.id"), 
        nullable=True, 
        index=True,
        comment="成绩产生时的年级ID（快照，不随学生升年级而变化）"
    )
    student_classroom_id_at_time = Column(
        Integer, 
        ForeignKey("classrooms.id"), 
        nullable=True, 
        index=True,
        comment="成绩产生时的班级ID（快照）"
    )
    student_number_at_time = Column(
        String(50), 
        nullable=True, 
        index=True,
        comment="成绩产生时的学号（快照）"
    )
    
    # 课程和班级（当前）
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    
    # 学期
    semester = Column(String(20), nullable=False, index=True)
    
    # ... 其他字段 ...
```

**设计说明**：
- `student_id`：使用稳定的用户ID，永不变化
- `student_grade_id_at_time`：记录成绩产生时的年级，即使学生升年级也不变
- `student_number_at_time`：记录成绩产生时的学号，用于追溯
- `classroom_id`：当前班级（用于查询和统计）

### 4. 学生身份匹配辅助表（可选）

```python
class StudentIdentityMatch(Base):
    """学生身份匹配辅助表（用于导入时的匹配缓存）"""
    
    __tablename__ = "student_identity_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 匹配键
    match_key = Column(String(200), nullable=False, unique=True, index=True)
    # 格式："{school_id}:{student_number}" 或 "{school_id}:{name}:{grade_id}"
    
    # 匹配到的学生
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 匹配类型
    match_type = Column(
        String(20), 
        nullable=False,
        comment="匹配类型：student_number, name_grade, id_card"
    )
    
    # 匹配置信度
    confidence = Column(Float, default=1.0, nullable=False, comment="匹配置信度（0-1）")
    
    # 最后更新时间
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关联关系
    student = relationship("User", foreign_keys=[student_id])
```

---

## 🔍 学生身份匹配策略

### 匹配优先级

```
1. 学籍号匹配（最高优先级，推荐）
   └─ student_registration_number（全国唯一，永久不变，置信度1.0）

2. 精确匹配
   └─ student_id (如果提供，置信度1.0)

3. 学号匹配
   ├─ 当前学号匹配（置信度0.95）
   └─ 历史学号匹配（在有效期内，置信度0.9）

4. 身份证号匹配（如果提供）
   └─ id_card_number（精确匹配，置信度1.0）

5. 姓名+年级匹配
   ├─ full_name + grade_id + school_id
   ├─ 单匹配：置信度0.9
   └─ 多匹配：需要人工确认

6. 模糊匹配（最低优先级）
   ├─ 姓名相似度匹配
   └─ 需要人工确认（置信度0.7以下）
```

### 匹配算法实现

```python
async def match_student(
    db: AsyncSession,
    student_registration_number: Optional[str] = None,  # 学籍号（最高优先级）
    student_id: Optional[int] = None,  # 学生ID
    student_number: Optional[str] = None,  # 学号
    student_name: Optional[str] = None,  # 姓名
    grade_id: Optional[int] = None,  # 年级ID
    school_id: Optional[int] = None,  # 学校ID
    id_card_number: Optional[str] = None,  # 身份证号
    semester: Optional[str] = None,  # 用于确定学号的有效期
) -> Optional[Tuple[User, float]]:
    """
    匹配学生身份
    
    返回: (User对象, 置信度) 或 None
    """
    
    # 1. 学籍号匹配（最高优先级，推荐方式）
    if student_registration_number:
        query = select(User).where(
            User.student_registration_number == student_registration_number,
            User.role == UserRole.STUDENT
        )
        student = await db.scalar(query)
        if student:
            return (student, 1.0)  # 学籍号匹配，置信度最高
    
    # 2. 精确匹配：student_id
    if student_id:
        student = await db.get(User, student_id)
        if student:
            return (student, 1.0)
    
    # 2. 学号匹配
    if student_number and school_id:
        # 2.1 当前学号匹配
        query = select(User).where(
            User.student_number == student_number,
            User.school_id == school_id
        )
        student = await db.scalar(query)
        if student:
            return (student, 1.0)
        
        # 2.2 历史学号匹配（如果提供了学期，可以确定学号的有效期）
        if semester:
            # 解析学期时间
            semester_date = parse_semester_date(semester)
            
            query = select(StudentNumberHistory).join(User).where(
                StudentNumberHistory.student_number == student_number,
                StudentNumberHistory.school_id == school_id,
                StudentNumberHistory.valid_from <= semester_date,
                or_(
                    StudentNumberHistory.valid_to.is_(None),
                    StudentNumberHistory.valid_to >= semester_date
                )
            )
            history = await db.scalar(query)
            if history:
                student = await db.get(User, history.student_id)
                if student:
                    return (student, 0.95)  # 历史匹配置信度略低
    
    # 3. 身份证号匹配
    if id_card_number:
        # 注意：身份证号应该加密存储，这里需要解密后匹配
        encrypted_id_card = encrypt(id_card_number)
        query = select(User).where(User.id_card_number == encrypted_id_card)
        student = await db.scalar(query)
        if student:
            return (student, 1.0)
    
    # 4. 姓名+年级匹配
    if student_name and grade_id and school_id:
        query = select(User).where(
            User.full_name == student_name,
            User.grade_id == grade_id,
            User.school_id == school_id,
            User.role == UserRole.STUDENT
        )
        students = await db.scalars(query).all()
        
        if len(students) == 1:
            return (students[0], 0.9)  # 单匹配，置信度较高
        elif len(students) > 1:
            # 多个匹配，需要人工确认
            return None  # 返回None，标记需要人工确认
    
    # 5. 模糊匹配（可选）
    if student_name and school_id:
        # 使用相似度算法（如Levenshtein距离）
        query = select(User).where(
            User.school_id == school_id,
            User.role == UserRole.STUDENT
        )
        all_students = await db.scalars(query).all()
        
        best_match = None
        best_score = 0.0
        
        for student in all_students:
            if student.full_name:
                similarity = calculate_similarity(student_name, student.full_name)
                if similarity > best_score and similarity > 0.8:  # 相似度阈值
                    best_score = similarity
                    best_match = student
        
        if best_match:
            return (best_match, best_score * 0.7)  # 模糊匹配置信度较低
    
    return None  # 未找到匹配
```

---

## 📥 成绩导入中的学生识别

### 导入文件格式扩展

**支持多种学生标识方式**：

**方式1：使用学籍号（推荐，最高优先级）**

| 学籍号 | 课程代码 | 成绩 | 满分 | 考试ID |
|--------|---------|------|------|--------|
| G1234567890123456789 | MATH_001 | 90 | 100 | final_2024_1 |
| G1234567890123456790 | MATH_001 | 88 | 100 | final_2024_1 |

**方式2：使用学号（学校内部学号）**

| 学号 | 学生姓名 | 年级 | 课程代码 | 成绩 | 满分 | 考试ID |
|------|---------|------|---------|------|------|--------|
| 2024001 | 张三 | 一年级 | MATH_001 | 90 | 100 | final_2024_1 |
| 2024002 | 李四 | 一年级 | MATH_001 | 88 | 100 | final_2024_1 |

**方式3：使用学生ID（系统内部ID）**

| 学生ID | 课程代码 | 成绩 | 满分 | 考试ID |
|--------|---------|------|------|--------|
| 123 | MATH_001 | 90 | 100 | final_2024_1 |
| 124 | MATH_001 | 88 | 100 | final_2024_1 |

### 导入流程中的匹配

```
1. 解析导入文件
   ↓
2. 对每一行数据，尝试匹配学生
   ├─ 如果提供student_id → 直接使用
   ├─ 如果提供学号 → 学号匹配
   ├─ 如果提供姓名+年级 → 姓名+年级匹配
   └─ 如果匹配失败 → 标记为需要人工确认
   ↓
3. 生成匹配报告
   ├─ 成功匹配数量
   ├─ 需要确认的匹配（低置信度）
   └─ 匹配失败的行
   ↓
4. 用户确认（如果需要）
   ├─ 查看匹配结果
   ├─ 手动修正匹配错误
   └─ 确认导入
   ↓
5. 创建成绩记录
   ├─ 使用匹配到的student_id
   ├─ 记录学籍号（用于精确关联）
   ├─ 记录成绩产生时的年级快照
   ├─ 记录成绩产生时的学号快照
   └─ 记录成绩产生时的班级快照
```

### 导入API扩展

```python
POST /api/v1/grades/records/import

{
    "file": <文件>,
    "matching_strategy": "auto|confirm|strict",
    # auto: 自动匹配，低置信度也接受
    # confirm: 需要确认低置信度匹配
    # strict: 只接受高置信度匹配
    
    "preview": true,  # 预览模式，返回匹配结果但不导入
}

响应：
{
    "preview": true,
    "total_rows": 120,
    "matched": 115,
    "needs_confirmation": 3,
    "failed": 2,
    "matching_results": [
        {
            "row": 1,
            "student_number": "2024001",
            "student_name": "张三",
            "matched_student_id": 123,
            "matched_student_name": "张三",
            "matched_student_registration_number": "G1234567890123456789",
            "confidence": 1.0,
            "match_type": "student_registration_number",  # 或 "student_number", "name_grade" 等
            "status": "matched"
        },
        {
            "row": 5,
            "student_number": "2024005",
            "student_name": "王五",
            "matched_student_id": null,
            "confidence": 0.0,
            "match_type": null,
            "status": "failed",
            "error": "未找到匹配的学生"
        },
        {
            "row": 8,
            "student_number": null,
            "student_name": "赵六",
            "grade": "一年级",
            "matched_student_id": 125,
            "matched_student_name": "赵六",
            "confidence": 0.9,
            "match_type": "name_grade",
            "status": "needs_confirmation",
            "warning": "存在重名，请确认"
        }
    ]
}
```

---

## 📊 历史成绩查询

### 查询设计

**查询学生所有成绩**（不考虑年级变化）：
```sql
SELECT * FROM grade_records 
WHERE student_id = 123
ORDER BY semester, created_at;
```

**查询学生在特定年级的成绩**：
```sql
SELECT * FROM grade_records 
WHERE student_id = 123 
  AND student_grade_id_at_time = 1  -- 一年级
ORDER BY semester, created_at;
```

**查询学生按学期和年级的成绩统计**：
```sql
SELECT 
    student_grade_id_at_time,
    semester,
    COUNT(*) as record_count,
    AVG(score) as avg_score
FROM grade_records 
WHERE student_id = 123
GROUP BY student_grade_id_at_time, semester
ORDER BY semester;
```

### API设计

```python
GET /api/v1/grades/records/student/{student_id}?grade_id={grade_id}&semester={semester}

# 查询参数：
# - grade_id: 可选，筛选特定年级的成绩（使用student_grade_id_at_time）
# - semester: 可选，筛选特定学期
# - include_history: 可选，是否包含历史年级的成绩（默认true）
```

---

## 🛠️ 实施建议

### 阶段一：数据模型扩展（1周）

1. **扩展User模型**
   - **增加`student_registration_number`字段（学籍号，必需）**
     - 全局唯一约束
     - 对于学生角色，设置为必需字段
     - 创建索引优化查询性能
   - 增加`student_number`字段（学号，可选）
   - 增加`id_card_number`字段（可选，加密存储）
   - 创建学号唯一性约束（学校内唯一）

2. **创建StudentNumberHistory模型**
   - 设计表结构
   - 编写迁移脚本
   - 创建索引

3. **扩展GradeRecord模型**
   - 增加`student_registration_number`字段（学籍号，用于精确关联）
   - 增加快照字段（`student_grade_id_at_time`等）
   - 更新唯一性约束
   - 创建索引（包括学籍号索引）

### 阶段二：匹配算法实现（1周）

1. **实现学生匹配函数**
   - 实现多维度匹配逻辑
   - 实现置信度计算
   - 编写单元测试

2. **实现学号历史管理**
   - 学号变更时自动记录历史
   - 实现历史查询功能

### 阶段三：导入功能增强（1周）

1. **扩展导入API**
   - 支持多种学生标识方式
   - 实现匹配预览功能
   - 实现匹配确认流程

2. **前端界面开发**
   - 匹配结果展示
   - 匹配确认界面
   - 手动匹配功能

### 阶段四：历史成绩查询（1周）

1. **实现历史成绩查询API**
   - 支持按年级筛选
   - 支持按学期筛选
   - 实现统计功能

2. **前端界面开发**
   - 历史成绩展示
   - 年级切换功能
   - 成绩趋势分析

### 数据迁移策略

1. **现有数据迁移**
   - 为现有成绩记录补充快照信息
   - 从User表获取当时的年级信息（如果可追溯）
   - 如果无法追溯，使用当前年级作为默认值

2. **学号历史初始化**
   - 为现有学生创建初始学号历史记录
   - `valid_from`设置为学生创建时间
   - `valid_to`设置为NULL（当前有效）

---

## 📝 总结

### 关键设计要点

1. **学籍号优先**：**学籍号（student_registration_number）作为主要的学生身份标识**，全国唯一、永久不变，是匹配的最高优先级
2. **稳定标识优先**：优先使用稳定的标识（学籍号 > User.id）关联学生
3. **历史快照**：成绩记录保存产生时的年级、学号等信息，不依赖当前状态，同时记录学籍号用于精确关联
4. **多维度匹配**：支持学籍号、学号、姓名+年级、身份证号等多种匹配方式
5. **变更追踪**：记录学号变化历史，支持历史匹配（学籍号不需要追踪，因为不变）
6. **置信度机制**：匹配结果包含置信度，低置信度需要人工确认

### 解决的问题

✅ **年级变化**：通过快照字段记录成绩产生时的年级，不受学生升年级影响  
✅ **学号变化**：通过学号历史记录和历史匹配，支持使用历史学号导入成绩  
✅ **身份识别**：**学籍号作为主要标识，全国唯一、永久不变，确保匹配的准确性和唯一性**  
✅ **历史追溯**：可以准确查询学生在不同年级的成绩记录  
✅ **跨系统对接**：学籍号是教育部门统一标准，便于与外部系统（如教育局统考系统）对接  

### 学籍号的使用优势

1. **唯一性保证**：全国范围内唯一，避免匹配错误
2. **永久不变**：不受转学、升年级、复学等任何情况影响
3. **业务友好**：比数据库自增ID更有业务意义，便于理解和沟通
4. **标准化**：符合教育部门标准，便于系统对接和数据交换
5. **追溯性强**：可以跨学校、跨地区追溯学生完整学习轨迹

该设计方案确保了成绩管理系统能够正确处理学生身份变化，保证数据的准确性和可追溯性。**使用学籍号作为主要标识，是解决学生身份识别问题的最佳方案。**
