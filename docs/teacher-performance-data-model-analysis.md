# 教师绩效数据模型分析报告

## 1. 当前教师数据存储方式

### 1.1 教师表结构
**结论：教师没有单独的表，使用统一的 `User` 表**

- **表名**: `users`
- **位置**: `backend/app/models/user.py`
- **角色标识**: 通过 `role` 字段，值为 `UserRole.TEACHER` 来标识教师

### 1.2 User 表结构（教师相关字段）

```python
class User(Base):
    __tablename__ = "users"
    
    # 基本信息
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(100), unique=True)
    full_name = Column(String(100))
    role = Column(SQLEnum(UserRole))  # TEACHER 标识教师
    
    # 组织关联（当前设计）
    region_id = Column(Integer, ForeignKey("regions.id"))      # 所属区/县
    school_id = Column(Integer, ForeignKey("schools.id"))        # 所属学校
    grade_id = Column(Integer, ForeignKey("grades.id"))          # 所属年级 ⚠️ 单个值
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))  # 所属班级 ⚠️ 单个值
```

## 2. 当前教师关联关系

### 2.1 已存在的关联

| 关联类型 | 实现方式 | 位置 | 说明 |
|---------|---------|------|------|
| 教师-学校 | `User.school_id` | `users` 表 | ✅ 直接关联，单个学校 |
| 教师-年级 | `User.grade_id` | `users` 表 | ⚠️ 只能存储单个年级 |
| 教师-班级 | `User.classroom_id` | `users` 表 | ⚠️ 只能存储单个班级 |
| 班主任-班级 | `Classroom.head_teacher_id`<br>`Classroom.deputy_head_teacher_id` | `classrooms` 表 | ✅ 支持正副班主任 |
| 教师-班级（多对多） | `ClassroomMembership` | `classroom_memberships` 表 | ✅ 支持多个班级，角色包括 `SUBJECT_TEACHER` |
| 教师-教研组 | `GroupMembership` | `group_memberships` 表 | ✅ 通过教研组间接关联学科 |

### 2.2 ClassroomMembership 表结构

```python
class ClassroomMembership(Base):
    __tablename__ = "classroom_memberships"
    
    id = Column(Integer, primary_key=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role_in_class = Column(SQLEnum(RoleInClass))  # 包括: SUBJECT_TEACHER
    is_active = Column(Boolean, default=True)
    
    # 唯一约束
    UniqueConstraint("classroom_id", "user_id")
```

**角色枚举**:
- `HEAD_TEACHER_PRIMARY` - 正班主任
- `HEAD_TEACHER_DEPUTY` - 副班主任
- `SUBJECT_TEACHER` - 学科教师
- `CADRE` - 班干部
- `STUDENT` - 学生

## 3. 问题分析

### 3.1 教师绩效统计需求

为了支持教师绩效功能，需要能够查询：
1. **教师任教的学科**：一个教师可能教多个学科（如：语文+历史）
2. **教师任教的年级**：一个教师可能教多个年级（如：七年级+八年级）
3. **教师任教的班级**：一个教师可能教多个班级（如：7年级1班、7年级2班）
4. **教师所属学校**：通常单个学校（已有 `school_id`）
5. **时间维度**：需要支持按学期/学年统计

### 3.2 当前设计的局限性

| 需求 | 当前支持 | 问题 |
|------|---------|------|
| 教师-学校 | ✅ `User.school_id` | 单个学校，满足需求 |
| 教师-年级 | ⚠️ `User.grade_id` | **只能存储单个年级，无法支持多年级教学** |
| 教师-班级 | ⚠️ `User.classroom_id`<br>✅ `ClassroomMembership` | `classroom_id` 只能单个，但 `ClassroomMembership` 支持多个 |
| 教师-学科 | ❌ 缺失 | **没有明确的教师-学科关联表** |
| 时间维度 | ❌ 缺失 | **没有学期/学年字段** |

### 3.3 关键问题

1. **缺少教师-学科关联表**
   - 无法直接查询"某教师教哪些学科"
   - 只能通过 `ClassroomMembership` + `Classroom` + `Subject` 间接查询

2. **缺少教师-年级关联表**
   - `User.grade_id` 只能存储单个值
   - 无法支持"某教师教七年级和八年级"的场景

3. **缺少时间维度**
   - 无法区分"2023-2024学年"和"2024-2025学年"的教学任务
   - 无法支持跨学年的绩效统计

## 4. 建议方案

### 方案一：创建教师教学任务表（推荐）

创建一个 `TeacherTeachingAssignment` 表，统一管理教师的教学任务：

```python
class TeacherTeachingAssignment(Base):
    """教师教学任务表（支持多学科、多年级、多班级）"""
    __tablename__ = "teacher_teaching_assignments"
    
    id = Column(Integer, primary_key=True)
    
    # 教师关联
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 组织关联
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    
    # 时间维度
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False, index=True)
    academic_year = Column(String(20), nullable=False, comment="学年，如 2023-2024")
    
    # 任务类型
    assignment_type = Column(
        SQLEnum(TeachingAssignmentType),
        nullable=False,
        comment="任务类型：HEAD_TEACHER(班主任)/SUBJECT_TEACHER(学科教师)"
    )
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    teacher = relationship("User", foreign_keys=[teacher_id])
    school = relationship("School")
    grade = relationship("Grade")
    classroom = relationship("Classroom")
    subject = relationship("Subject")
    semester = relationship("Semester")
    
    # 唯一约束：同一学期，同一教师，同一班级，同一学科只能有一条记录
    __table_args__ = (
        UniqueConstraint(
            'teacher_id', 'semester_id', 'classroom_id', 'subject_id',
            name='uq_teacher_semester_classroom_subject'
        ),
        Index('idx_teacher_semester', 'teacher_id', 'semester_id'),
        Index('idx_school_grade_subject', 'school_id', 'grade_id', 'subject_id'),
    )
```

**优点**：
- ✅ 统一管理所有教学任务
- ✅ 支持多学科、多年级、多班级
- ✅ 支持时间维度（学期/学年）
- ✅ 便于绩效统计查询

**缺点**：
- ⚠️ 需要数据迁移，将现有 `ClassroomMembership` 数据迁移到新表
- ⚠️ 需要维护两套数据（或逐步替换）

### 方案二：扩展现有 ClassroomMembership 表

在 `ClassroomMembership` 表中添加学科和时间字段：

```python
class ClassroomMembership(Base):
    # ... 现有字段 ...
    
    # 新增字段
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=True, index=True)
    academic_year = Column(String(20), nullable=True, comment="学年")
    
    # 修改唯一约束
    __table_args__ = (
        UniqueConstraint(
            "classroom_id", "user_id", "subject_id", "semester_id",
            name="uq_classroom_user_subject_semester"
        ),
    )
```

**优点**：
- ✅ 复用现有表结构
- ✅ 迁移成本较低

**缺点**：
- ⚠️ 对于学生记录，`subject_id` 和 `semester_id` 可能为空，语义不够清晰
- ⚠️ 表结构混合了学生和教师的数据，不够纯粹

### 方案三：创建独立的教师-学科关联表

创建 `TeacherSubject` 表，专门管理教师-学科关系：

```python
class TeacherSubject(Base):
    """教师-学科关联表"""
    __tablename__ = "teacher_subjects"
    
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    teacher = relationship("User", foreign_keys=[teacher_id])
    subject = relationship("Subject")
    school = relationship("School")
    semester = relationship("Semester")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('teacher_id', 'subject_id', 'semester_id', name='uq_teacher_subject_semester'),
    )
```

**优点**：
- ✅ 结构清晰，专门用于教师-学科关联
- ✅ 支持时间维度

**缺点**：
- ⚠️ 需要配合 `ClassroomMembership` 使用，才能知道教师教哪些班级
- ⚠️ 数据分散在多个表中，查询需要 JOIN

## 5. 推荐方案：方案一（TeacherTeachingAssignment）

### 5.1 设计理由

1. **统一管理**：一个表管理所有教学任务，便于查询和统计
2. **支持多维度**：同时关联学校、年级、班级、学科、学期
3. **绩效统计友好**：可以直接按教师、学科、年级、学期等维度统计
4. **扩展性好**：未来可以添加课时数、教学评价等字段

### 5.2 数据迁移策略

1. **从 ClassroomMembership 迁移**：
   - 查询所有 `role_in_class = 'SUBJECT_TEACHER'` 的记录
   - 根据 `classroom_id` 获取年级和学校信息
   - 需要确定学科信息（可能需要手动补充或从其他数据源获取）

2. **从 Classroom 迁移**：
   - 查询所有 `head_teacher_id` 和 `deputy_head_teacher_id`
   - 创建班主任类型的教学任务记录

3. **保留现有表**：
   - 暂时保留 `ClassroomMembership` 用于学生管理
   - 逐步迁移教师相关数据到新表

### 5.3 查询示例

```python
# 查询某教师在某学期的所有教学任务
assignments = session.query(TeacherTeachingAssignment).filter(
    TeacherTeachingAssignment.teacher_id == teacher_id,
    TeacherTeachingAssignment.semester_id == semester_id
).all()

# 查询某学校某年级某学科的所有教师
teachers = session.query(User).join(TeacherTeachingAssignment).filter(
    TeacherTeachingAssignment.school_id == school_id,
    TeacherTeachingAssignment.grade_id == grade_id,
    TeacherTeachingAssignment.subject_id == subject_id,
    TeacherTeachingAssignment.semester_id == semester_id
).all()

# 统计某教师的教学班级数
classroom_count = session.query(func.count(distinct(TeacherTeachingAssignment.classroom_id))).filter(
    TeacherTeachingAssignment.teacher_id == teacher_id,
    TeacherTeachingAssignment.semester_id == semester_id
).scalar()
```

## 6. 实施建议

### 6.1 阶段一：创建新表
1. 创建 `TeacherTeachingAssignment` 模型
2. 创建数据库迁移文件
3. 执行迁移

### 6.2 阶段二：数据迁移
1. 编写迁移脚本，从现有数据源导入
2. 验证数据完整性
3. 更新相关 API 和业务逻辑

### 6.3 阶段三：功能集成
1. 更新教师管理界面，支持教学任务管理
2. 更新绩效统计功能，使用新表查询
3. 逐步废弃 `User.grade_id` 和 `User.classroom_id` 的使用（仅用于学生）

## 7. 总结

**当前状态**：
- ✅ 教师基本信息存储在 `User` 表
- ✅ 教师-学校关联：`User.school_id`
- ⚠️ 教师-年级关联：`User.grade_id`（仅支持单个）
- ⚠️ 教师-班级关联：`ClassroomMembership`（支持多个，但缺少学科和时间维度）
- ❌ 教师-学科关联：缺失

**建议**：
- 创建 `TeacherTeachingAssignment` 表，统一管理教师教学任务
- 支持多学科、多年级、多班级、多学期的教学任务
- 为教师绩效统计提供完整的数据基础
