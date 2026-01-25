# 学生成绩管理系统设计方案

## 📋 目录

1. [设计概述](#设计概述)
2. [系统架构](#系统架构)
3. [数据模型设计](#数据模型设计)
4. [功能模块设计](#功能模块设计)
5. [API设计](#api设计)
6. [前端界面设计](#前端界面设计)
7. [实施计划](#实施计划)

---

## 🎯 设计概述

### 设计目标

基于现有的InspireEd探究式STEM教学平台，设计一个**过程性与终结性相结合**的学生成绩管理系统，实现：

1. **多维度成绩管理**：整合活动提交、课堂表现、项目作业、考试等各类成绩
2. **智能成绩计算**：支持自定义成绩权重配置，自动计算总评成绩
3. **数据驱动分析**：提供班级、年级、学校多层级成绩统计分析
4. **无缝系统集成**：充分利用现有的ActivitySubmission、FormativeAssessment等数据
5. **灵活成绩配置**：支持不同课程、不同学期的成绩计算规则

### 设计原则

- **复用现有数据**：充分利用ActivitySubmission、FormativeAssessment等现有模型
- **扩展性优先**：设计灵活的成绩类型和权重配置系统
- **数据一致性**：确保成绩数据与活动提交数据的一致性
- **权限控制**：严格的角色权限管理（教师、学生、管理员）
- **可追溯性**：记录成绩变更历史，支持成绩审核流程

---

## 🏗️ 系统架构

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│              成绩管理前端界面 (Vue3)                      │
│  - 成绩录入/编辑                                         │
│  - 成绩查询/统计                                         │
│  - 成绩报表/导出                                         │
└─────────────────────────────────────────────────────────┘
                            ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│              成绩管理API层 (FastAPI)                     │
│  - 成绩CRUD操作                                          │
│  - 成绩计算引擎                                          │
│  - 统计分析服务                                          │
│  - 成绩通知服务                                          │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│              数据模型层 (SQLAlchemy)                     │
│  - GradeRecord (成绩记录)                                │
│  - GradeCategory (成绩类别)                              │
│  - GradeWeight (成绩权重配置)                            │
│  - GradeStatistics (成绩统计)                            │
│  - GradeHistory (成绩历史)                               │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│              现有数据源                                   │
│  - ActivitySubmission (活动提交)                         │
│  - FormativeAssessment (过程性评估)                      │
│  - ClassSession (课堂会话)                               │
│  - Lesson (教案)                                         │
│  - Course (课程)                                         │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

- **后端**：FastAPI + SQLAlchemy + Alembic（与现有系统一致）
- **数据库**：PostgreSQL（复用现有数据库）
- **前端**：Vue3 + TypeScript + Pinia（与现有系统一致）
- **实时通知**：WebSocket（复用现有WebSocket服务）

### 命名规范

为了保持前后端命名一致性，**统一使用 snake_case（蛇形命名）**：

#### 后端命名规范

1. **数据库模型（SQLAlchemy）**
   - 表名：`grade_categories`, `grade_records`, `grade_summaries`
   - 字段名：`student_id`, `course_id`, `max_score`, `teacher_feedback`, `created_at`

2. **Pydantic Schemas（API请求/响应）**
   - 类名：`GradeRecordResponse`, `GradeCategoryCreate`, `GradeWeightUpdate`
   - 字段名：`student_id`, `course_id`, `max_score`, `teacher_feedback`, `created_at`
   - **注意**：不使用 `serialization_alias`，直接使用 `snake_case`

3. **Python代码**
   - 变量名：`grade_record`, `student_id`, `max_score`
   - 函数名：`calculate_total_score`, `sync_from_activities`
   - 常量名：`MAX_SCORE`, `DEFAULT_WEIGHT`

#### 前端命名规范

1. **TypeScript接口定义**
   ```typescript
   interface GradeRecord {
     id: number
     student_id: number
     course_id: number
     max_score: number
     teacher_feedback?: string
     created_at: string
   }
   ```

2. **Vue组件中的使用**
   ```typescript
   // 使用 snake_case
   const gradeRecord = ref<GradeRecord>({
     student_id: 123,
     course_id: 456,
     max_score: 100
   })
   
   // API调用
   const response = await api.get(`/grades/records/${gradeRecord.value.student_id}`)
   ```

3. **变量命名**
   - 变量名：`grade_record`, `student_id`, `max_score`
   - 函数名：`calculateTotalScore`, `syncFromActivities`（函数名可以使用camelCase，但API字段使用snake_case）

#### 命名规范检查清单

- ✅ 数据库表名和字段名：`snake_case`
- ✅ API请求/响应字段：`snake_case`
- ✅ TypeScript接口字段：`snake_case`
- ✅ JSON数据字段：`snake_case`
- ✅ 函数名：后端 `snake_case`，前端 `camelCase`（JavaScript惯例）
- ✅ 类名：`PascalCase`（Python和TypeScript惯例）

#### 示例对比

**❌ 不推荐（前后端不一致）**
```python
# 后端
class GradeRecord(BaseModel):
    student_id: int
    max_score: float
```

```typescript
// 前端
interface GradeRecord {
  studentId: number  // ❌ 使用camelCase
  maxScore: number   // ❌ 使用camelCase
}
```

**✅ 推荐（前后端一致）**
```python
# 后端
class GradeRecord(BaseModel):
    student_id: int
    max_score: float
```

```typescript
// 前端
interface GradeRecord {
  student_id: number  // ✅ 使用snake_case
  max_score: number   // ✅ 使用snake_case
}
```

#### 为什么选择 snake_case？

1. **符合Python和数据库惯例**：Python PEP 8推荐使用snake_case，PostgreSQL等数据库也使用snake_case
2. **后端代码已大量使用**：现有系统后端已广泛使用snake_case，改动最小
3. **API一致性**：RESTful API通常使用snake_case，符合行业惯例
4. **前端兼容性**：TypeScript/JavaScript可以很好地处理snake_case，只需统一接口定义

---

## 📊 数据模型设计

### 存储方式设计决策

#### 问题：宽存储 vs 短存储

**宽存储**：一个学生一次考试的所有科目成绩作为一个记录
- 优点：一次考试一条记录，查询一次考试的所有成绩更快
- 缺点：
  - 不够灵活，科目数量变化时需要修改表结构
  - 不符合数据库范式，难以扩展
  - 科目数量不固定时会造成大量NULL字段
  - 难以支持不同考试包含不同科目的情况

**短存储（推荐）**：一个科目一个记录（当前设计）
- 优点：
  - 灵活，易于扩展新科目
  - 符合数据库第三范式，数据规范化
  - 易于查询单个科目成绩
  - 支持不同考试包含不同科目
  - 便于统计和分析
- 缺点：
  - 一次考试需要多条记录（但可以通过`exam_id`字段关联）

#### 最终决策：采用短存储 + 考试关联字段

为了同时支持灵活性和关联性，在`GradeRecord`模型中增加`exam_id`字段，用于关联同一考试的不同科目成绩：

```python
# 在GradeRecord中增加
exam_id = Column(String(100), nullable=True, index=True)  # 考试ID，用于关联同一考试的不同科目成绩
exam_name = Column(String(200), nullable=True)  # 考试名称，如"2024-2025学年第一学期期末统考"
```

这样设计的好处：
1. **保持灵活性**：每个科目独立存储，易于扩展
2. **支持关联查询**：通过`exam_id`可以快速查询一次考试的所有科目成绩
3. **支持批量导入**：导入期末统考成绩时，可以为同一考试的所有科目设置相同的`exam_id`
4. **便于统计分析**：可以按考试维度进行统计分析

#### 示例数据

**期末统考成绩存储示例**：
```
exam_id: "final_exam_2024_2025_1"
exam_name: "2024-2025学年第一学期期末统考"

记录1: student_id=1, course_id=1(语文), exam_id="final_exam_2024_2025_1", score=85
记录2: student_id=1, course_id=2(数学), exam_id="final_exam_2024_2025_1", score=90
记录3: student_id=1, course_id=3(英语), exam_id="final_exam_2024_2025_1", score=88
```

查询一次考试的所有成绩：
```sql
SELECT * FROM grade_records 
WHERE exam_id = 'final_exam_2024_2025_1' AND student_id = 1;
```

### 1. GradeCategory（成绩类别）

定义成绩的类型和来源，如：平时成绩、期中考试、期末考试、项目作业等。

```python
class GradeCategory(Base):
    """成绩类别模型"""
    
    __tablename__ = "grade_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 平时成绩、期中考试、期末考试等
    code = Column(String(50), nullable=False, unique=True)  # daily, midterm, final, project
    description = Column(Text, nullable=True)
    
    # 数据来源类型
    source_type = Column(
        SQLEnum(GradeSourceType),
        nullable=False,
        comment="数据来源：manual(手动录入), activity(活动提交), auto(自动计算)"
    )
    
    # 是否启用
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 显示顺序
    display_order = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class GradeSourceType(str, Enum):
    """成绩来源类型"""
    MANUAL = "manual"  # 手动录入
    ACTIVITY = "activity"  # 从活动提交自动获取
    AUTO = "auto"  # 自动计算（如总评成绩）


### 2. GradeWeight（成绩权重配置）

定义不同成绩类别在总评成绩中的权重，支持按课程、学期、班级等维度配置。

```python
class GradeWeight(Base):
    """成绩权重配置模型"""
    
    __tablename__ = "grade_weights"
    __table_args__ = (
        UniqueConstraint("course_id", "classroom_id", "semester", "category_id", 
                        name="uq_grade_weight_scope"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 适用范围
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True, index=True)  # NULL表示全校通用
    semester = Column(String(20), nullable=False, index=True)  # 2024-2025-1, 2024-2025-2
    
    # 成绩类别
    category_id = Column(Integer, ForeignKey("grade_categories.id"), nullable=False, index=True)
    
    # 权重配置
    weight = Column(Float, nullable=False, comment="权重（0-1之间，所有类别权重之和应为1）")
    max_score = Column(Float, nullable=False, comment="该类别满分")
    
    # 是否计入总评
    is_included = Column(Boolean, default=True, nullable=False)
    
    # 配置说明
    description = Column(Text, nullable=True)
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # 关联关系
    course = relationship("Course")
    classroom = relationship("Classroom")
    category = relationship("GradeCategory")
    creator = relationship("User", foreign_keys=[created_by])
```


### 3. GradeRecord（成绩记录）

存储学生的具体成绩数据，支持多种数据来源。

```python
class GradeRecord(Base):
    """成绩记录模型"""
    
    __tablename__ = "grade_records"
    __table_args__ = (
        # 唯一性约束：同一学生、同一课程、同一班级、同一学期、同一类别、同一项目的成绩唯一
        # 注意：如果item_id为NULL，则通过exam_id区分；如果exam_id也为NULL，则同一类别只能有一条记录
        UniqueConstraint("student_id", "course_id", "classroom_id", "semester", 
                        "category_id", "item_id", name="uq_grade_record"),
        # 索引优化
        Index("idx_grade_student_course", "student_id", "course_id"),
        Index("idx_grade_classroom_semester", "classroom_id", "semester"),
        Index("idx_grade_registration_number", "student_registration_number"),
        Index("idx_grade_exam", "exam_id", "student_id"),
        Index("idx_grade_semester_grade", "semester", "student_grade_id_at_time"),
        Index("idx_grade_semester_stream", "semester", "student_stream_type_at_time"),
        Index("idx_grade_status", "status", "recorded_at"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 学生信息（使用稳定的student_id，永不变化）
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 成绩产生时的快照信息（不依赖User的当前状态）
    # 这些字段记录成绩产生时的状态，即使学生升年级、换班级也不变
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
        comment="成绩产生时的学号（快照，用于追溯）"
    )

    # 高中分科快照（用于文科/理科分科统计与分科排名，避免学生后续调整分科导致历史统计漂移）
    # 取值约定：all(未分科/不区分), arts(文科), science(理科)
    student_stream_type_at_time = Column(
        String(20),
        nullable=True,
        index=True,
        comment="成绩产生时的分科类型（快照）：all/arts/science"
    )
    
    # 课程和班级（当前，用于查询和统计）
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    
    # 学期
    semester = Column(String(20), nullable=False, index=True)  # 2024-2025-1
    
    # 成绩类别
    category_id = Column(Integer, ForeignKey("grade_categories.id"), nullable=False, index=True)
    
    # 具体项目（可选，用于区分同一类别下的不同项目）
    # 例如：平时成绩类别下可能有"作业1"、"作业2"等多个项目
    item_id = Column(String(100), nullable=True, index=True)  # lesson_123, activity_456
    item_name = Column(String(200), nullable=True)  # "第一章作业", "期中考试"
    
    # 考试关联（用于关联同一考试的不同科目成绩）
    # 例如：期末统考时，同一学生的所有科目成绩共享相同的exam_id
    exam_id = Column(String(100), nullable=True, index=True, comment="考试ID，用于关联同一考试的不同科目成绩")
    exam_name = Column(String(200), nullable=True, comment="考试名称，如'2024-2025学年第一学期期末统考'")
    
    # 导入来源信息（可选，用于追踪导入记录）
    import_batch_id = Column(
        String(100), 
        nullable=True, 
        index=True, 
        comment="导入批次ID，用于追踪同一批导入的记录"
    )
    import_source = Column(
        String(50), 
        nullable=True, 
        comment="导入来源：excel, csv, json, api"
    )
    
    # 成绩数据
    score = Column(Float, nullable=False, comment="实际得分")
    max_score = Column(Float, nullable=False, comment="满分")
    percentage = Column(Float, nullable=True, comment="百分比得分（score/max_score）")
    
    # 数据来源
    source_type = Column(
        SQLEnum(GradeSourceType),
        nullable=False,
        comment="数据来源类型"
    )
    source_id = Column(Integer, nullable=True, comment="来源ID（如ActivitySubmission.id）")
    
    # 状态
    status = Column(
        SQLEnum(GradeStatus),
        default=GradeStatus.DRAFT,
        nullable=False,
        index=True,
        comment="成绩状态：draft(草稿), confirmed(已确认), locked(已锁定)"
    )
    
    # 备注
    remark = Column(Text, nullable=True)
    
    # 是否计入总评（某些成绩可能不计入总评，如补考成绩、重修成绩等）
    is_included_in_total = Column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="是否计入总评成绩"
    )
    
    # 录入信息
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 审核信息（可选）
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # 关联关系
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course")
    classroom = relationship("Classroom")
    category = relationship("GradeCategory")
    recorder = relationship("User", foreign_keys=[recorded_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class GradeStatus(str, Enum):
    """成绩状态"""
    DRAFT = "draft"  # 草稿
    CONFIRMED = "confirmed"  # 已确认
    LOCKED = "locked"  # 已锁定（不可修改）
```


### 3.1 StudentStreamAssignment（学生学期分科归属：权威来源）

为支持“高中分科统计/分科排名”，系统需要一个**权威的分科归属数据源**（以“学生在某学校某学期的分科归属”为准），并在成绩记录中保留快照（`student_stream_type_at_time`）防止历史数据漂移。

```python
class StudentStreamType(str, Enum):
    ALL = "all"        # 未分科/不区分
    ARTS = "arts"      # 文科
    SCIENCE = "science"  # 理科


class StudentStreamAssignment(Base):
    """学生学期分科归属（权威来源）"""
    
    __tablename__ = "student_stream_assignments"
    __table_args__ = (
        UniqueConstraint("school_id", "student_id", "semester", name="uq_student_stream_assignment"),
        Index("idx_stream_assignment_school_semester", "school_id", "semester"),
        Index("idx_stream_assignment_stream", "school_id", "semester", "stream_type"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 范围（按学校差异化）
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    
    # 学生
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 学期
    semester = Column(String(20), nullable=False, index=True)
    
    # 分科归属
    stream_type = Column(SQLEnum(StudentStreamType), nullable=False, default=StudentStreamType.ALL, index=True)
    
    # 数据来源（可选）：manual/import/api 等，便于审计
    source = Column(String(50), nullable=True)
    source_detail = Column(JSON, nullable=True, default=dict)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

**分科归属与快照写入规则（强制规定）**：
- 当系统计算/生成 `GradeSummary`、`GradeStatistics`、分科排名时，分科归属来源优先级：
  1. `StudentStreamAssignment`（权威归属）
  2. `GradeRecord.student_stream_type_at_time`（历史快照兜底/用于审计对照）
  3. 若两者都缺失，视为 `all`
- 导入外部成绩时：
  - 若导入文件包含分科字段（文/理），应同步写入 `StudentStreamAssignment`（按 school+student+semester upsert）
  - 同时将该分科写入导入产生/更新的 `GradeRecord.student_stream_type_at_time`

### 4. GradeSummary（成绩汇总）

存储学生的总评成绩和各类别成绩汇总，便于快速查询。

```python
class GradeSummary(Base):
    """成绩汇总模型（按学生-课程-学期汇总）"""
    
    __tablename__ = "grade_summaries"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", "classroom_id", "semester",
                        name="uq_grade_summary"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 学生信息
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 课程和班级
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    
    # 学期
    semester = Column(String(20), nullable=False, index=True)
    
    # 各类别成绩（JSON格式）
    # 示例：
    # {
    #   "daily": {"score": 85, "max_score": 100, "weight": 0.3, "percentage": 0.85},
    #   "midterm": {"score": 90, "max_score": 100, "weight": 0.3, "percentage": 0.90},
    #   "final": {"score": 88, "max_score": 100, "weight": 0.4, "percentage": 0.88}
    # }
    category_scores = Column(JSON, nullable=False, default=dict)
    
    # 总评成绩
    total_score = Column(Float, nullable=True, comment="总评得分")
    total_max_score = Column(Float, nullable=True, comment="总评满分")
    total_percentage = Column(Float, nullable=True, comment="总评百分比")
    
    # 等级（可选）
    grade_level = Column(String(10), nullable=True, comment="等级：A+, A, B+, B, C+, C, D, F")
    
    # 排名信息
    rank_in_class = Column(Integer, nullable=True, comment="班级排名")
    rank_in_grade = Column(Integer, nullable=True, comment="年级排名")
    
    # 统计信息
    total_items = Column(Integer, default=0, nullable=False, comment="成绩项总数")
    completed_items = Column(Integer, default=0, nullable=False, comment="已完成项数")
    
    # 最后更新时间
    last_calculated_at = Column(DateTime, nullable=True, comment="最后计算时间")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # 关联关系
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course")
    classroom = relationship("Classroom")
```


### 5. GradeStatistics（成绩统计）

存储班级、年级、学校等层级的成绩统计数据，用于快速查询和分析。

```python
class GradeStatistics(Base):
    """成绩统计模型"""
    
    __tablename__ = "grade_statistics"
    __table_args__ = (
        UniqueConstraint("scope_type", "scope_id", "course_id", "semester", "category_id",
                        name="uq_grade_statistics"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 统计范围
    scope_type = Column(
        String(20),
        nullable=False,
        index=True,
        comment="统计范围：classroom(班级), grade(年级), school(学校), region(区域)"
    )
    scope_id = Column(Integer, nullable=False, index=True, comment="范围ID")
    
    # 课程和学期
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    semester = Column(String(20), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("grade_categories.id"), nullable=True, index=True)  # NULL表示总评
    
    # 统计指标
    total_students = Column(Integer, default=0, nullable=False, comment="学生总数")
    valid_students = Column(Integer, default=0, nullable=False, comment="有效成绩学生数")
    
    # 成绩分布
    average_score = Column(Float, nullable=True, comment="平均分")
    median_score = Column(Float, nullable=True, comment="中位数")
    highest_score = Column(Float, nullable=True, comment="最高分")
    lowest_score = Column(Float, nullable=True, comment="最低分")
    std_deviation = Column(Float, nullable=True, comment="标准差")
    
    # 等级分布（JSON格式）
    # 示例：{"A+": 5, "A": 10, "B+": 15, "B": 8, "C+": 2, "C": 0, "D": 0, "F": 0}
    grade_distribution = Column(JSON, nullable=True, default=dict)
    
    # 分数段分布（JSON格式）
    # 示例：{"90-100": 15, "80-89": 20, "70-79": 10, "60-69": 5, "0-59": 0}
    score_distribution = Column(JSON, nullable=True, default=dict)
    
    # 通过率（如果设置了及格线）
    pass_rate = Column(Float, nullable=True, comment="通过率（0-1）")
    pass_score = Column(Float, nullable=True, comment="及格分数线")
    
    # 最后更新时间
    last_calculated_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # 关联关系
    course = relationship("Course")
    category = relationship("GradeCategory")
```


### 6. GradeHistory（成绩历史）

记录成绩的变更历史，支持审核和追溯。

```python
class GradeHistory(Base):
    """成绩变更历史模型"""
    
    __tablename__ = "grade_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    grade_record_id = Column(Integer, ForeignKey("grade_records.id"), nullable=False, index=True)
    
    # 变更信息
    old_score = Column(Float, nullable=True, comment="原成绩")
    new_score = Column(Float, nullable=True, comment="新成绩")
    old_status = Column(String(20), nullable=True, comment="原状态")
    new_status = Column(String(20), nullable=True, comment="新状态")
    
    # 变更原因
    change_reason = Column(Text, nullable=True, comment="变更原因")
    
    # 操作信息
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 变更类型
    change_type = Column(
        String(20),
        nullable=False,
        comment="变更类型：create(创建), update(更新), delete(删除), confirm(确认), lock(锁定)"
    )
    
    # 关联关系
    grade_record = relationship("GradeRecord", back_populates="histories")
    changer = relationship("User", foreign_keys=[changed_by])
```


### 7. GradeThresholdConfig（阈值/分数线配置：K9 各率 + 高中分数线）

用于配置小学/初中（K9）的“通过/优秀/良好/低分”阈值，以及高中可自定义的“分数线”（如 985线、本科线、专科线等）。支持不同学校使用不同线（并支持更细粒度覆盖）。

```python
class GradeThresholdKind(str, Enum):
    K9_RATE = "k9_rate"        # 小学/初中：用于计算通过率/优秀率/良好率/低分率
    HS_LINE = "hs_line"        # 高中：自定义分数线（985线、本科线、专科线等），用于计算上线率


class GradeThresholdCode(str, Enum):
    # K9 默认各率
    PASS = "pass"
    EXCELLENT = "excellent"
    GOOD = "good"
    LOW = "low"

    # 高中常用分数线（示例，允许继续扩展）
    LINE_985 = "line_985"                # 985线
    LINE_BACHELOR = "line_bachelor"      # 本科线
    LINE_JUNIOR_COLLEGE = "line_junior"  # 专科线


class GradeThresholdConfig(Base):
    """分数线配置（按学校差异化，可逐级覆盖）"""
    
    __tablename__ = "grade_threshold_configs"
    __table_args__ = (
        UniqueConstraint(
            "school_id", "grade_id", "course_id", "semester", "category_id", "threshold_kind", "threshold_code",
            name="uq_grade_threshold_config_scope",
        ),
        Index("idx_threshold_school_semester", "school_id", "semester"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 范围：按学校差异化（必填）
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    
    # 可选细粒度覆盖：不填表示“全校通用/全学段通用/所有课程通用”
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)
    semester = Column(String(20), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("grade_categories.id"), nullable=True, index=True)  # NULL 表示总评
    
    threshold_kind = Column(SQLEnum(GradeThresholdKind), nullable=False, index=True)
    threshold_code = Column(String(50), nullable=False, index=True, comment="阈值/分数线代码（支持自定义）")
    threshold_name = Column(String(100), nullable=True, comment="展示名称，如“985线/本科线/专科线”")
    
    # 统一用百分比存储（0-1），避免满分差异导致混乱
    threshold_percentage = Column(Float, nullable=False, comment="阈值百分比（0-1）")
    
    # 备注与审计
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

**阈值查找优先级（从高到低）**：
1. school + grade + course + semester + category
2. school + grade + course + semester + (category=NULL)
3. school + grade + (course=NULL) + semester + category
4. school + (grade=NULL) + (course=NULL) + semester + (category=NULL)

### 8. GradeImportBatch / GradeImportBatchItem（导入批次审计与一键撤销）

为保证“批次导入后发现错误可以一键撤销”，必须将“导入造成的变更”以批次维度记录清楚（创建/更新了哪些记录、更新前是什么、更新后是什么）。

```python
class GradeImportBatchStatus(str, Enum):
    CREATED = "created"         # 已创建（文件已上传/解析完成）
    COMMITTED = "committed"     # 已导入生效
    ROLLED_BACK = "rolled_back" # 已撤销


class GradeImportBatch(Base):
    __tablename__ = "grade_import_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    import_batch_id = Column(String(100), nullable=False, unique=True, index=True)  # 供 GradeRecord 关联
    
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    semester = Column(String(20), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("grade_categories.id"), nullable=True, index=True)
    exam_id = Column(String(100), nullable=True, index=True)
    exam_name = Column(String(200), nullable=True)
    
    # 导入参数快照（覆盖/跳过策略、错误处理等）
    import_config = Column(JSON, nullable=False, default=dict)
    
    # 统计与错误摘要（便于导入历史页面展示）
    total_rows = Column(Integer, default=0, nullable=False)
    imported = Column(Integer, default=0, nullable=False)
    updated = Column(Integer, default=0, nullable=False)
    skipped = Column(Integer, default=0, nullable=False)
    errors = Column(Integer, default=0, nullable=False)
    error_report = Column(JSON, nullable=True, default=dict)
    
    status = Column(SQLEnum(GradeImportBatchStatus), default=GradeImportBatchStatus.CREATED, nullable=False, index=True)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    committed_at = Column(DateTime, nullable=True)
    rolled_back_at = Column(DateTime, nullable=True)


class GradeImportBatchItemAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    SKIP = "skip"


class GradeImportBatchItem(Base):
    __tablename__ = "grade_import_batch_items"
    __table_args__ = (
        Index("idx_import_batch_item_batch", "import_batch_id"),
        Index("idx_import_batch_item_record", "grade_record_id"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    import_batch_id = Column(String(100), nullable=False, index=True)
    
    action = Column(SQLEnum(GradeImportBatchItemAction), nullable=False)
    grade_record_id = Column(Integer, ForeignKey("grade_records.id"), nullable=True, index=True)
    
    # 回滚所需快照：更新前/更新后（JSON 存全量字段，便于回滚与审计）
    before_data = Column(JSON, nullable=True, default=dict)
    after_data = Column(JSON, nullable=True, default=dict)
    
    # 行号与错误（可选）
    source_row_number = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

**一键撤销规则（强制规定）**：
- 仅允许撤销 `status=committed` 且尚未撤销的批次。
- 撤销前检查：若批次影响的任意 `GradeRecord.status = locked`，则拒绝撤销，并返回不可撤销记录清单。
- 撤销动作：
  - `action=create`：将该 `GradeRecord` 软删除（或删除）并写入 `GradeHistory(change_type="rollback_delete")`
  - `action=update`：用 `before_data` 还原该 `GradeRecord` 并写入 `GradeHistory(change_type="rollback_update")`
- 撤销后：批次 `status` 置为 `rolled_back`，记录 `rolled_back_at`；同时触发相关 `GradeSummary/GradeStatistics` 重算（仅影响到的学生/课程/班级范围）。

### 数据模型关系图

```
GradeCategory (成绩类别)
    ↓ (1:N)
GradeWeight (权重配置) ←→ Course, Classroom
    ↓
GradeRecord (成绩记录) ←→ Student, Course, Classroom, Category
    ↓ (1:N)
GradeHistory (变更历史)
    ↓
GradeSummary (成绩汇总) ←→ Student, Course, Classroom
    ↓
GradeStatistics (成绩统计) ←→ Course, Category
```

---

## 🎯 功能模块设计

### 1. 成绩配置管理

#### 1.1 成绩类别管理
- **功能**：创建和管理成绩类别（平时成绩、期中考试、期末考试等）
- **权限**：管理员、教研员
- **操作**：
  - 创建/编辑/删除成绩类别
  - 设置数据来源类型（手动/自动）
  - 配置显示顺序

#### 1.2 权重配置管理
- **功能**：为不同课程、班级、学期配置成绩权重
- **权限**：教师、管理员
- **操作**：
  - 创建/编辑权重配置
  - 验证权重总和是否为1
  - 支持复制配置到其他班级/学期
  - 查看配置历史

### 2. 成绩录入管理

#### 2.1 手动成绩录入
- **功能**：教师手动录入学生成绩
- **权限**：教师
- **操作**：
  - 批量录入成绩（支持Excel导入）
  - 单个学生成绩录入/编辑
  - 成绩确认和锁定
  - 成绩审核流程

#### 2.2 自动成绩同步
- **功能**：从ActivitySubmission自动同步成绩
- **权限**：系统自动
- **操作**：
  - 定时任务同步活动提交成绩
  - 支持手动触发同步
  - 同步日志和错误处理
  - 数据一致性校验

#### 2.3 外部成绩导入（期末统考等）
- **功能**：导入外部系统的成绩数据，如期末统考、区域统考等
- **权限**：教师、管理员、教研员
- **支持格式**：
  - Excel格式（推荐）
  - CSV格式
  - JSON格式（API导入）
- **功能点**：
  - 批量导入多个学生的多个科目成绩
  - 支持按考试关联（通过exam_id）
  - **智能学生身份匹配**：
    - **优先使用学籍号匹配**（全国唯一，永久不变，最高优先级）
    - 支持多种学生标识方式（学籍号、学号、姓名+年级、学生ID、身份证号）
    - 自动匹配学生身份，支持历史学号匹配
    - 匹配置信度评估，低置信度需要人工确认
    - 匹配结果预览和确认
  - 数据校验（学生ID、课程ID、成绩范围等）
  - 重复数据检测和处理（覆盖/跳过/报错）
  - 导入预览和确认
  - 导入日志和错误报告
  - **导入批次审计与一键撤销（强制支持）**：
    - 每次导入必须生成一个 `import_batch_id`（UUID/雪花ID），并将批次元信息写入 `GradeImportBatch`（见下文数据模型）
    - 导入历史页面可按批次查看：操作者、时间、导入参数（覆盖/跳过策略）、错误报告、实际导入/更新/跳过数量等
    - **一键撤销本批次**：将本批次导入对成绩数据造成的变更完整回滚（创建的记录删除/软删除，更新的记录恢复到更新前）
    - **撤销前置条件（保证“锁定不可变”）**：若本批次影响的任意 `GradeRecord.status = locked`，则拒绝撤销，并返回不可撤销记录清单与原因
    - 撤销接口需幂等：批次已撤销时重复调用不应再次改动数据
  - 支持增量导入和全量导入
  - **年级和学号变化处理**：
    - 自动记录成绩产生时的年级快照
    - 自动记录成绩产生时的学号快照
    - 支持通过历史学号匹配学生
- **导入模板示例**：
  ```
  方式1：使用学籍号（推荐，最高优先级）
  学籍号 | 课程代码 | 成绩 | 满分 | 考试ID | 考试名称
  -------|---------|------|------|--------|----------
  G1234567890123456789 | MATH_001 | 90 | 100 | final_2024_1 | 2024-2025学年第一学期期末统考
  
  方式2：使用学号（学校内部学号）
  学号 | 学生姓名 | 年级 | 课程代码 | 课程名称 | 成绩 | 满分 | 考试ID | 考试名称
  ----|---------|------|---------|---------|------|------|--------|----------
  2024001 | 张三 | 一年级 | MATH_001 | 数学 | 90 | 100 | final_2024_1 | 2024-2025学年第一学期期末统考
  
  方式3：使用学生ID（系统内部ID）
  学生ID | 课程代码 | 成绩 | 满分 | 考试ID
  -------|---------|------|------|----------
  123 | MATH_001 | 90 | 100 | final_2024_1
  ```

#### 2.4 成绩计算引擎
- **功能**：根据权重配置自动计算总评成绩
- **权限**：系统自动
- **操作**：
  - 实时计算总评成绩
  - 支持多种计算规则（加权平均、等级制等）
  - 成绩排名计算
  - 等级转换（百分制转等级制）

##### 2.4.1 统计口径与强制规则（统一口径）

> 本节口径用于：`GradeSummary` 总评、`GradeStatistics` 统计、分析系统所有“及格率/优秀率/良好率/低分预警”等指标，必须保持一致。

**(1) 有效成绩记录（valid record）**
- 默认仅统计/计算满足以下条件的 `GradeRecord`：
  - `status` ∈ {`confirmed`, `locked`}
  - `is_included_in_total = true`
- `draft` 仅用于教师录入过程的预览，不进入正式汇总/统计口径。

**(2) 缺考/缺项处理：按权重归一化（缺考不按 0 分硬扣）**
- 记某学生在某课程/班级/学期下，配置的“计入总评”的类别集合为 \(C\)，每个类别权重为 \(w_c\)（来自 `GradeWeight` 且 `is_included=true`）。
- 对于每个类别 \(c\)，取该学生在该类别下的有效成绩记录集合 \(R_c\)：
  - 若 \(R_c\) 为空（即该类别缺考/缺项），则该类别在本次总评计算中视为“缺失类别”，**不直接按 0 分计入**。
  - 若 \(R_c\) 非空，则该类别百分比得分定义为：
    - `category_percentage(c) = sum(score) / sum(max_score)`
    - 说明：同类别多条记录按满分汇总计算，天然支持“一个类别下有多个作业/测验”。
- 总评百分比得分采用归一化加权：
  - \(W = \sum\limits_{c \in C, R_c \neq \emptyset} w_c\)
  - 若 \(W = 0\)，则 `total_percentage = null`（总评不可计算），`completed_items = 0`
  - 否则：
    - `total_percentage = ( Σ (w_c * category_percentage(c)) ) / W`

**(3) 总评满分与换算**
- `total_max_score` 默认 100（后续可配置）。
- `total_score = round(total_percentage * total_max_score, 2)`（用于展示/导出）。

**(4) 精度与四舍五入（避免排名抖动）**
- 内部计算与排名比较：`percentage`、`total_percentage` 以 **4 位小数**保存/比较（如 0.8770）。
- 对外展示：分数/百分比统一 **2 位小数**展示（如 87.70 / 87.70%）。

**(5) 并列排名规则**
- 排名基于 `total_percentage`（或指定 `category_id` 时基于该类别百分比）。
- 并列规则：同分（按 4 位小数比较）视为并列。
- 排名方式：**竞赛排名（Competition Ranking）**：
  - 例：分数 [100, 99, 99, 98] → 名次 [1, 2, 2, 4]
- 列表展示稳定性：并列内部可按 `student_registration_number`（学籍号）或 `student_id` 升序排序，但**名次不变**。

**(6) 学段口径：小学/初中（K9）用“各率”，高中用“分数线（可自定义）”**

- **小学/初中（K9）常用指标**（用于班级/年级/学校统计与预警）：
  - 通过率（pass）
  - 优秀率（excellent）
  - 良好率（good）
  - 低分率（low，用于预警）
- **高中常用指标：分数线体系（可自定义）**：
  - 高中不固定使用“优秀/良好/通过/低分”四条线，而是以“分数线/上线率”为核心指标。
  - 分数线支持完全自定义（例如常见：**985线、本科线、专科线**；也可扩展为“211线、一本线、二本线”等）。
  - 每条分数线都可生成对应“上线率”：`line_rate(threshold_code) = total_percentage >= line_threshold_percentage`
- **阈值/分数线配置规则**（统一配置模型，按学校差异化）：
  - `school_id` 必填（支持不同学校不同线）
  - 可选细粒度覆盖：school → grade → course → semester → category（类别/总评）
  - 阈值统一以 `percentage`（0-1）作为判定依据；UI 可允许输入“分数”，后台用当前 `total_max_score` 或 `max_score` 换算为 percentage 保存（见下文 `GradeThresholdConfig`）。

**(7) 各率/上线率口径（统一分母）**
- 分母：`valid_students` = 总评可计算（`total_percentage != null`）的学生数量。
- 分子（K9 各率）：
  - `pass_rate`：`total_percentage >= pass_line`
  - `excellent_rate`：`total_percentage >= excellent_line`
  - `good_rate`：`total_percentage >= good_line`
  - `low_rate`：`total_percentage < low_line`
- 分子（高中“分数线-上线率”）：
  - `line_rate(threshold_code)`：`total_percentage >= line_threshold_percentage`
- 若某条线未配置，则对应指标返回 `null`（或不展示），避免默认值误导。

**(8) 高中文理分科排名/统计（分科维度）**
- 高中统计与排名必须支持 `stream_type`（文科/理科）维度：
  - 在“年级排名/年级统计”中，可选择：
    - `stream_type=arts`（文科）仅在文科范围内排名/统计
    - `stream_type=science`（理科）仅在理科范围内排名/统计
    - `stream_type=all`（默认）全体学生排名/统计
- `stream_type` 的来源以“学生在该学期的分科归属”为准，建议在成绩记录中保存快照（避免学生后续调整分科导致历史统计漂移）。

### 3. 成绩查询与统计

#### 3.1 学生成绩查询
- **功能**：学生查看自己的成绩
- **权限**：学生
- **功能点**：
  - 查看各科目成绩
  - 查看成绩明细（各类别成绩）
  - 查看成绩趋势图
  - 查看班级/年级排名
  - **个人成绩变化**：支持按学期/考试维度查看分数、排名、上线率/各率变化（K9 各率或高中分数线）
  - 成绩通知提醒

#### 3.2 教师成绩管理
- **功能**：教师管理所教班级的成绩
- **权限**：教师
- **功能点**：
  - 查看班级成绩列表
  - 成绩统计分析（平均分、及格率、分布图等）
  - 成绩导出（Excel、PDF）
  - 成绩对比分析（班级间、学期间）
  - **教师带班成绩变化**：支持查看“自己所带班级”的平均分、各率/上线率、排名等随时间变化趋势
  - 学生成绩预警（低分提醒）

#### 3.3 管理员统计分析
- **功能**：多层级成绩统计分析
- **权限**：管理员、教研员
- **功能点**：
  - 班级/年级/学校成绩统计
  - 成绩趋势分析
  - 科目对比分析
  - 教师教学效果分析
  - **学校成绩变化**：按学期/考试查看学校整体指标变化（平均分、分布、各率/上线率）
  - **分数线与各率变化**：支持查看“不同时期学校的分数线变化”以及基于该线的上线率/各率随时间变化
  - **教师带班变化看板**：支持按教师维度查看其带班指标随时间变化（用于教学效果追踪）
  - 数据可视化报表

### 4. 成绩报表与导出

#### 4.1 成绩单生成
- **功能**：生成标准格式的成绩单
- **支持格式**：
  - Excel格式（支持批量导出）
  - PDF格式（支持打印）
  - 自定义模板

#### 4.2 统计分析报表
- **功能**：生成各类统计分析报表
- **报表类型**：
  - 班级成绩分析报表
  - 学生个人成绩报告
  - 科目成绩对比报表
  - 学期成绩趋势报表

### 5. 成绩通知与提醒

#### 5.1 成绩发布通知
- **功能**：成绩录入/更新后通知学生
- **通知方式**：
  - 系统内消息通知
  - WebSocket实时推送
  - 邮件通知（可选）

#### 5.2 成绩预警提醒
- **功能**：低分、缺考等异常情况提醒
- **提醒对象**：
  - 学生本人
  - 任课教师
  - 班主任（可选）

---

## 🔌 API设计

### API路由结构

```
/api/v1/grades/
├── categories/          # 成绩类别管理
│   ├── GET /           # 获取成绩类别列表
│   ├── POST /          # 创建成绩类别
│   ├── GET /{id}       # 获取成绩类别详情
│   ├── PUT /{id}       # 更新成绩类别
│   └── DELETE /{id}    # 删除成绩类别
│
├── weights/            # 权重配置管理
│   ├── GET /           # 获取权重配置列表
│   ├── POST /          # 创建权重配置
│   ├── GET /{id}       # 获取权重配置详情
│   ├── PUT /{id}       # 更新权重配置
│   ├── DELETE /{id}    # 删除权重配置
│   └── POST /copy      # 复制权重配置
│
├── thresholds/         # 分数线/等级线配置
│   ├── GET /           # 获取分数线配置列表（支持按 school/grade/course/semester/category 筛选）
│   ├── POST /          # 创建/更新分数线配置（upsert）
│   ├── GET /resolve    # 获取“某学校/年级/课程/学期/类别”最终生效的阈值（按优先级合并）
│   └── DELETE /{id}    # 删除分数线配置
│
├── records/            # 成绩记录管理
│   ├── GET /           # 获取成绩记录列表（支持多维度筛选）
│   ├── POST /          # 创建成绩记录
│   ├── POST /bulk      # 批量创建成绩记录
│   ├── GET /{id}       # 获取成绩记录详情
│   ├── PUT /{id}       # 更新成绩记录
│   ├── DELETE /{id}    # 删除成绩记录
│   ├── POST /{id}/confirm  # 确认成绩
│   ├── POST /{id}/lock     # 锁定成绩
│   ├── POST /sync-from-activities  # 从活动提交同步成绩
│   ├── POST /import    # 导入外部成绩（Excel/CSV/JSON）
│   ├── POST /import/preview  # 预览导入数据（不实际导入）
│   ├── GET /import/batches   # 导入批次列表/历史
│   ├── GET /import/batches/{import_batch_id}  # 导入批次详情（含明细与错误报告）
│   ├── POST /import/batches/{import_batch_id}/rollback  # 一键撤销本批次
│   └── GET /by-exam/{exam_id}  # 按考试ID查询成绩记录
│
├── summaries/          # 成绩汇总查询
│   ├── GET /           # 获取成绩汇总列表
│   ├── GET /student/{student_id}  # 获取学生成绩汇总
│   ├── GET /classroom/{classroom_id}  # 获取班级成绩汇总
│   ├── POST /calculate  # 手动触发成绩计算
│   └── GET /export     # 导出成绩汇总
│
├── statistics/         # 成绩统计分析
│   ├── GET /classroom/{classroom_id}  # 班级成绩统计
│   ├── GET /grade/{grade_id}           # 年级成绩统计
│   ├── GET /school/{school_id}          # 学校成绩统计
│   ├── GET /trend                      # 成绩趋势分析
│   └── GET /comparison                 # 成绩对比分析
│
└── history/            # 成绩历史记录
    ├── GET /           # 获取成绩变更历史
    └── GET /{grade_record_id}  # 获取特定成绩记录的变更历史
```

### 核心API示例

#### 1. 创建成绩记录

```python
POST /api/v1/grades/records/
{
    "student_id": 123,
    "course_id": 456,
    "classroom_id": 789,
    "semester": "2024-2025-1",
    "category_id": 1,
    "item_id": "lesson_123",
    "item_name": "第一章作业",
    "score": 85.0,
    "max_score": 100.0,
    "source_type": "manual",
    "remark": "作业完成质量良好"
}
```

#### 2. 批量同步活动提交成绩

```python
POST /api/v1/grades/records/sync-from-activities
{
    "lesson_id": 123,
    "cell_id": 456,
    "category_id": 1,
    "semester": "2024-2025-1",
    "classroom_id": 789
}
```

#### 3. 获取学生成绩汇总

```python
GET /api/v1/grades/summaries/student/123?course_id=456&semester=2024-2025-1
```

响应：
```json
{
    "student_id": 123,
    "student_name": "张三",
    "course_id": 456,
    "course_name": "一年级数学",
    "classroom_id": 789,
    "classroom_name": "一年级一班",
    "semester": "2024-2025-1",
    "category_scores": {
        "daily": {
            "score": 85.0,
            "max_score": 100.0,
            "weight": 0.3,
            "percentage": 0.85
        },
        "midterm": {
            "score": 90.0,
            "max_score": 100.0,
            "weight": 0.3,
            "percentage": 0.90
        },
        "final": {
            "score": 88.0,
            "max_score": 100.0,
            "weight": 0.4,
            "percentage": 0.88
        }
    },
    "total_score": 87.7,
    "total_max_score": 100.0,
    "total_percentage": 0.877,
    "grade_level": "B+",
    "rank_in_class": 5,
    "rank_in_grade": 25
}
```

#### 4. 导入期末统考成绩

```python
POST /api/v1/grades/records/import
Content-Type: multipart/form-data

{
    "file": <Excel/CSV文件>,
    "exam_id": "final_exam_2024_2025_1",  # 可选，如果不提供则自动生成
    "exam_name": "2024-2025学年第一学期期末统考",  # 可选
    "category_id": 3,  # 成绩类别ID（如"期末考试"）
    "semester": "2024-2025-1",
    "overwrite_existing": false,  # 是否覆盖已存在的成绩
    "skip_errors": true  # 遇到错误时是否跳过继续导入
}
```

响应：
```json
{
    "success": true,
    "total_rows": 120,
    "imported": 115,
    "skipped": 3,
    "errors": 2,
    "exam_id": "final_exam_2024_2025_1",
    "errors_detail": [
        {
            "row": 5,
            "student_id": "2024005",
            "course_id": "MATH_001",
            "error": "学生不存在"
        },
        {
            "row": 12,
            "student_id": "2024012",
            "course_id": "CHINESE_001",
            "error": "成绩超出范围：150（满分100）"
        }
    ],
    "warnings": [
        {
            "row": 8,
            "message": "成绩已存在，已跳过（如需覆盖请设置overwrite_existing=true）"
        }
    ]
}
```

#### 5. 按考试ID查询成绩

```python
GET /api/v1/grades/records/by-exam/final_exam_2024_2025_1?student_id=123
```

响应：
```json
{
    "exam_id": "final_exam_2024_2025_1",
    "exam_name": "2024-2025学年第一学期期末统考",
    "student_id": 123,
    "student_name": "张三",
    "records": [
        {
            "id": 1001,
            "course_id": 1,
            "course_name": "语文",
            "score": 85.0,
            "max_score": 100.0,
            "percentage": 0.85
        },
        {
            "id": 1002,
            "course_id": 2,
            "course_name": "数学",
            "score": 90.0,
            "max_score": 100.0,
            "percentage": 0.90
        }
    ],
    "total_courses": 2,
    "average_score": 87.5
}
```

#### 6. 获取班级成绩统计

```python
GET /api/v1/grades/statistics/classroom/789?course_id=456&semester=2024-2025-1
```

响应：
```json
{
    "classroom_id": 789,
    "classroom_name": "一年级一班",
    "course_id": 456,
    "course_name": "一年级数学",
    "semester": "2024-2025-1",
    "total_students": 40,
    "valid_students": 38,
    "average_score": 82.5,
    "median_score": 83.0,
    "highest_score": 98.0,
    "lowest_score": 45.0,
    "std_deviation": 12.3,
    "grade_distribution": {
        "A+": 5,
        "A": 10,
        "B+": 15,
        "B": 6,
        "C+": 2,
        "C": 0,
        "D": 0,
        "F": 0
    },
    "pass_rate": 0.95,
    "pass_score": 60.0
}
```

---

## 🎨 前端界面设计

### 1. 学生端界面

#### 1.1 我的成绩页面
- **布局**：卡片式布局，按课程分类展示
- **功能**：
  - 课程成绩卡片（显示总评成绩、等级、排名）
  - 点击查看成绩明细
  - 成绩趋势图表
  - 筛选功能（按学期、课程）

#### 1.2 成绩明细页面
- **布局**：表格 + 图表
- **内容**：
  - 各类别成绩明细表
  - 成绩分布雷达图
  - 成绩趋势折线图
  - 班级/年级排名对比

### 2. 教师端界面

#### 2.1 成绩管理首页
- **布局**：仪表盘布局
- **内容**：
  - 快速统计卡片（平均分、及格率、优秀率）
  - 成绩分布图表
  - 待录入成绩提醒
  - 最近操作记录

#### 2.2 成绩录入页面
- **布局**：表格编辑界面
- **功能**：
  - Excel导入/导出
  - 批量编辑
  - 单个学生成绩录入
  - 成绩确认和锁定
  - 数据校验提示

#### 2.3 外部成绩导入页面
- **布局**：文件上传 + 预览 + 确认
- **功能**：
  - 文件上传（支持Excel、CSV、JSON）
  - 导入模板下载
  - 数据预览（导入前预览）
  - 数据校验提示
  - 考试信息设置（exam_id、exam_name）
  - 导入选项配置（覆盖/跳过、错误处理策略）
  - 导入进度显示
  - 导入结果报告（成功/失败统计、错误详情）
  - 导入历史记录

#### 2.4 成绩统计分析页面
- **布局**：多图表展示
- **内容**：
  - 成绩分布直方图
  - 成绩趋势折线图
  - 科目对比柱状图
  - 学生排名列表
  - 成绩预警列表

#### 2.5 权重配置页面
- **布局**：表单 + 预览
- **功能**：
  - 权重配置表单
  - 权重总和验证
  - 配置预览
  - 配置历史记录

### 3. 管理员端界面

#### 3.1 成绩统计看板
- **布局**：多维度数据看板
- **内容**：
  - 全校成绩概览
  - 年级/班级对比
  - 科目成绩分析
  - 教师教学效果分析
  - 成绩趋势分析

#### 3.2 成绩类别管理页面
- **布局**：列表 + 表单
- **功能**：
  - 成绩类别列表
  - 创建/编辑类别
  - 类别启用/禁用
  - 类别使用统计

---

## 📅 实施计划

### 阶段一：基础数据模型（2周）

1. **数据库设计**
   - 创建GradeCategory、GradeWeight、GradeRecord等数据模型
   - 编写Alembic迁移脚本
   - 创建数据库索引优化查询性能

2. **基础API开发**
   - 实现成绩类别CRUD API
   - 实现权重配置CRUD API
   - 实现基础的成绩记录CRUD API

### 阶段二：成绩录入与计算（3周）

1. **成绩录入功能**
   - 实现手动成绩录入API
   - 实现批量导入功能
   - 实现从ActivitySubmission自动同步成绩
   - **实现外部成绩导入功能**（期末统考等）
     - Excel/CSV/JSON文件解析
     - 数据校验（学生ID、课程ID、成绩范围等）
     - 批量创建成绩记录
     - 导入日志和错误处理
     - 导入预览功能

2. **成绩计算引擎**
   - 实现总评成绩计算逻辑
   - 实现成绩排名计算
   - 实现等级转换功能

3. **成绩汇总功能**
   - 实现GradeSummary自动更新
   - 实现成绩汇总查询API
   - 实现按考试ID查询成绩功能

### 阶段三：统计分析功能（2周）

1. **成绩统计API**
   - 实现班级/年级/学校成绩统计
   - 实现成绩趋势分析
   - 实现成绩对比分析

2. **数据可视化**
   - 集成图表库（ECharts）
   - 实现各类统计图表

### 阶段四：前端界面开发（3周）

1. **学生端界面**
   - 我的成绩页面
   - 成绩明细页面

2. **教师端界面**
   - 成绩管理首页
   - 成绩录入页面
   - **外部成绩导入页面**（新增）
     - 文件上传组件
     - 导入模板下载
     - 数据预览表格
     - 导入配置表单
     - 导入结果展示
   - 成绩统计分析页面
   - 权重配置页面

3. **管理员端界面**
   - 成绩统计看板
   - 成绩类别管理页面

### 阶段五：高级功能（2周）

1. **成绩通知功能**
   - 集成WebSocket实时通知
   - 实现成绩发布通知
   - 实现成绩预警提醒

2. **成绩导出功能**
   - 实现Excel导出
   - 实现PDF导出
   - 实现自定义模板导出

3. **成绩历史与审核**
   - 实现成绩变更历史记录
   - 实现成绩审核流程

---

## ✅ 验收标准（强制口径 + 一键撤销）

> 用于保证“缺考归一化、并列排名、可配置分数线、批次撤销”在实现后可客观验收，避免口径偏差。

### 1) 缺考/缺项按权重归一化

- **场景**：权重配置：daily=0.3, midterm=0.3, final=0.4（均计入总评）。学生仅有 final 一项，final 百分比=0.80。
- **期望**：
  - 归一化权重总和 \(W=0.4\)
  - `total_percentage = (0.4*0.80)/0.4 = 0.80`
  - `total_score = 80.00`（total_max_score=100）

### 2) 并列排名（竞赛排名）

- **场景**：同一范围内 `total_percentage` 为 [1.0000, 0.9900, 0.9900, 0.9800]
- **期望排名**：[1, 2, 2, 4]

### 3) 分数线可配置且按学校生效

- **场景**：
  - 学校A：pass=0.60
  - 学校B：pass=0.50
  - 同一班级统计范围内，学生 `total_percentage` 分布相同
- **期望**：
  - 学校A、学校B 的 `pass_rate` 计算结果不同，并且都严格按各自阈值线判定

### 4) 阈值覆盖优先级

- **场景**：同一 school/semester 下同时存在：
  - school+grade+course+category 的配置
  - school+grade+course+category=NULL 的配置
- **期望**：优先命中更细粒度配置（category 级别优先于总评/默认）。

### 5) 导入批次一键撤销（含覆盖场景）

- **场景**：
  - 导入批次 B1 创建了一条新 `GradeRecord`（action=create）
  - 导入批次 B1 覆盖更新了一条已有 `GradeRecord`（action=update），并记录 before/after 快照
- **期望**：
  - 调用撤销：create 的记录被删除/软删除；update 的记录恢复到导入前（before_data）
  - 撤销后触发相关 `GradeSummary/GradeStatistics` 重算，页面统计与排名同步恢复
  - 批次撤销接口幂等：重复撤销不应产生二次变更

### 6) 撤销与锁定冲突

- **场景**：批次 B1 影响到的任意 `GradeRecord.status=locked`
- **期望**：撤销请求被拒绝，并返回不可撤销记录明细（保证锁定不可变）。

### 阶段六：测试与优化（2周）

1. **功能测试**
   - 单元测试
   - 集成测试
   - 端到端测试

2. **性能优化**
   - 数据库查询优化
   - 缓存策略优化
   - 前端性能优化

3. **文档完善**
   - API文档
   - 用户手册
   - 开发文档

---

## 🔒 权限控制

### 角色权限矩阵

| 功能 | 学生 | 教师 | 教研员 | 管理员 |
|------|------|------|--------|--------|
| 查看自己的成绩 | ✅ | - | - | - |
| 查看班级成绩 | - | ✅ | ✅ | ✅ |
| 录入成绩 | - | ✅ | ✅ | ✅ |
| 编辑成绩 | - | ✅ | ✅ | ✅ |
| 删除成绩 | - | ❌ | ✅ | ✅ |
| 锁定成绩 | - | ✅ | ✅ | ✅ |
| 配置权重 | - | ✅ | ✅ | ✅ |
| 管理成绩类别 | - | ❌ | ✅ | ✅ |
| 查看全校统计 | - | ❌ | ✅ | ✅ |
| 导出成绩报表 | - | ✅ | ✅ | ✅ |
| 导入外部成绩 | - | ✅ | ✅ | ✅ |

---

## 🔄 数据同步策略

### 1. 从ActivitySubmission同步成绩

**触发时机**：
- 活动提交被评分后（status变为GRADED）
- 定时任务批量同步（每天凌晨）
- 手动触发同步

**同步规则**：
- 根据lesson_id和cell_id匹配对应的成绩类别配置
- 如果存在对应的权重配置，自动创建GradeRecord
- 如果成绩已存在，根据配置决定是否更新

### 2. 成绩计算触发

**触发时机**：
- 成绩记录创建/更新后
- 权重配置更新后
- 定时任务批量计算（每天凌晨）

**计算流程**：
1. 获取学生的所有成绩记录
2. 根据权重配置计算各类别加权得分
3. 计算总评成绩
4. 更新GradeSummary
5. 重新计算排名
6. 更新GradeStatistics

---

## 📊 性能优化建议

### 1. 数据库优化

- **索引策略**：
  - 在student_id、course_id、classroom_id、semester等常用查询字段上创建索引
  - 创建复合索引优化多条件查询
  - 定期分析查询性能，优化慢查询

- **分区策略**：
  - GradeHistory表可按时间分区
  - GradeStatistics表可按学期分区

### 2. 缓存策略

- **Redis缓存**：
  - 缓存成绩汇总数据（GradeSummary）
  - 缓存统计数据（GradeStatistics）
  - 缓存权重配置（GradeWeight）
  - 设置合理的过期时间（如1小时）

### 3. 异步处理

- **异步任务**：
  - 成绩计算使用异步任务队列（Celery）
  - 成绩同步使用后台任务
  - 统计报表生成使用异步任务

---

## 🚀 未来扩展方向

1. **AI成绩分析**
   - 基于历史数据预测学生成绩趋势
   - 智能识别学习风险学生
   - 个性化学习建议生成

2. **多维度评估**
   - 整合过程性评估数据
   - 支持能力维度评估（如计算思维、创新能力等）
   - 支持同伴互评成绩

3. **成绩预测与干预**
   - 基于学习行为数据预测成绩
   - 自动触发学习干预措施
   - 个性化学习路径推荐

4. **家长端功能**
   - 家长查看学生成绩
   - 成绩通知推送
   - 家校沟通功能

---

## 📝 总结

本设计方案基于现有的InspireEd平台，充分利用了现有的数据模型和架构，设计了一个**过程性与终结性相结合**的学生成绩管理系统。系统具有以下特点：

1. **数据复用**：充分利用ActivitySubmission、FormativeAssessment等现有数据
2. **灵活配置**：支持多维度成绩类别和权重配置
3. **智能计算**：自动计算总评成绩和排名
4. **多层级统计**：支持班级、年级、学校多层级统计分析
5. **权限控制**：严格的角色权限管理
6. **可追溯性**：完整的成绩变更历史记录
7. **外部数据导入**：支持导入期末统考等外部成绩数据
8. **灵活的存储设计**：采用短存储方式，通过exam_id关联同一考试的不同科目成绩
9. **学生身份管理**：支持年级和学号变化，通过快照机制保证历史成绩的准确性

### 关键设计决策

1. **存储方式**：采用**短存储**（一个科目一个记录），通过`exam_id`字段关联同一考试的不同科目成绩，既保持了灵活性又支持关联查询。

2. **外部成绩导入**：支持Excel/CSV/JSON格式导入，特别针对期末统考等批量成绩导入场景进行了优化，支持数据预览、校验和错误处理。

3. **考试关联**：通过`exam_id`和`exam_name`字段，可以方便地查询和管理一次考试的所有科目成绩，便于统计分析和报表生成。

4. **年级和学号变化处理**：
   - **学籍号优先**：**学籍号（student_registration_number）作为主要的学生身份标识**，全国唯一、永久不变，是匹配的最高优先级
   - **历史快照机制**：成绩记录保存产生时的年级、学号等信息（`student_grade_id_at_time`、`student_number_at_time`），不依赖学生当前状态，同时记录学籍号用于精确关联
   - **稳定标识优先**：优先使用稳定的标识（学籍号 > User.id）关联学生
   - **多维度匹配**：支持学籍号、学号、姓名+年级、学生ID、身份证号等多种方式匹配学生
   - **学号历史追踪**：通过`StudentNumberHistory`模型记录学号变化历史，支持历史学号匹配（学籍号不需要追踪，因为不变）
   - **智能匹配算法**：自动匹配学生身份，提供置信度评估，低置信度匹配需要人工确认

### 相关设计文档

- **成绩存储方式与外部导入功能设计**：`docs/design/GRADE_STORAGE_AND_IMPORT_DESIGN.md`
- **学生身份识别与年级变化处理设计**：`docs/design/GRADE_STUDENT_IDENTIFICATION_DESIGN.md`
- **成绩存储设计完整性检查**：`docs/design/GRADE_RECORD_COMPLETENESS_CHECK.md`
- **学生成绩分析系统设计**：`docs/design/GRADE_ANALYSIS_DESIGN.md`

### 设计完整性说明

学生成绩存储设计已经比较完善，涵盖了：

1. **核心功能**：
   - ✅ 学生身份识别（学籍号优先）
   - ✅ 年级和学号变化处理（快照机制）
   - ✅ 多种数据来源支持（手动、自动、活动）
   - ✅ 完整的审核和追溯机制
   - ✅ 考试关联和批量导入支持

2. **数据完整性**：
   - ✅ 所有必需字段已定义
   - ✅ 外键约束完整
   - ✅ 唯一性约束合理
   - ✅ 索引优化完善

3. **扩展性**：
   - ✅ 支持导入追踪（import_batch_id, import_source）
   - ✅ 支持是否计入总评（is_included_in_total）
   - ✅ 预留扩展空间

**建议在实施时**：
- 根据实际业务需求，可以添加成绩等级字段（grade_level）
- 根据数据量大小，考虑分区策略
- 根据查询频率，优化索引策略

该设计方案为后续的系统实施提供了清晰的指导，可以根据实际需求分阶段实施。