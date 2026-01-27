# 教学增值评价功能 PRD

## 1. 产品概述

### 1.1 功能简介
教学增值评价（Value-Added Evaluation）是一种基于学生学业成绩进步情况的教育质量评价方法。与传统的绝对成绩评价不同，增值评价关注的是学生、教师或学校在一定时期内的**相对进步幅度**，而非绝对分数。

### 1.2 核心价值
- **公平性**：消除学生起点差异影响，评价教师/学校真实贡献
- **激励性**：关注进步过程，激发教师教学积极性
- **科学性**：基于统计模型，多因素综合分析
- **导向性**：引导关注教学改进，而非唯分数论

### 1.3 应用场景
| 场景 | 评价对象 | 核心指标 |
|------|---------|---------|
| 教师教学质量评价 | 教师 | 学生平均进步分、增值达标率 |
| 学校办学质量评估 | 学校 | 整体增值分数、学科增值排名 |
| 学生成长追踪 | 学生 | 个人进步曲线、学科增值 |
| 教育政策制定 | 区域 | 区域增值对比分析 |

---

## 2. 数据模型映射分析

### 2.1 新增表 vs 现有模型映射

| 新文档表结构 | 现有系统模型 | 映射关系 | 处理方式 |
|-------------|------------|---------|---------|
| `Region` | `Region` | ✅ 完全对应 | 无需修改，现有模型已支持 |
| `School` | `School` | ✅ 完全对应 | 无需修改 |
| `Grade` | `Grade` | ✅ 完全对应 | 无需修改 |
| `Class` | `Classroom` | ⚠️ 名称差异 | 映射：Class → Classroom |
| `Student` | `User` (role=student) | ⚠️ 设计差异 | 扩展 User 模型，添加 student_id_number |
| `Teacher` | `User` (role=teacher) | ⚠️ 设计差异 | 扩展 User 模型 |
| `Subject` | `Subject` | ✅ 完全对应 | 无需修改 |
| `Semester` | ❌ 不存在 | ❌ 缺失 | **新增模型** |
| `Exam` | ❌ 不存在 | ❌ 缺失 | **新增模型** |
| `Score` | ❌ 不存在 | ❌ 缺失 | **新增模型** |
| `EvaluationMetrics` | ❌ 不存在 | ❌ 缺失 | **新增模型** |
| `ValueAddedEvaluation` | ❌ 不存在 | ❌ 缺失 | **新增模型** |
| `StatisticalAnalysis` | ❌ 不存在 | ❌ 缺失 | **新增模型** |
| `Family` | ❌ 不存在 | ❌ 缺失 | **新增模型**（可选） |
| `TeacherTeam` | ❌ 不存在 | ❌ 缺失 | **新增模型**（可选） |
| `SubjectRelation` | ❌ 不存在 | ❌ 缺失 | **新增模型**（可选） |
| `StudentHistory` | ❌ 不存在 | ❌ 缺失 | **新增模型**（可选） |
| `TeacherHistory` | ❌ 不存在 | ❌ 缺失 | **新增模型**（可选） |
| `SubjectScore` | ❌ 不存在 | ❌ 缺失 | **新增模型**（可选） |

### 2.2 现有模型增强需求

#### User 模型增强（已有 `student_id_number` 字段）
现有 `User` 模型已包含 `student_id_number` 字段（学籍号/身份证号），可直接用于增值评价的学生追踪。

#### Classroom 模型映射
现有 `Classroom` 模型字段与新文档 `Class` 表的映射关系：
- `class_id` → `id`
- `class_name` → `name`
- `grade_id` → `grade_id` ✅
- `teacher_id` → `head_teacher_id` ✅
- `capacity` → ❌ 需新增
- `status` → `is_active` ✅

---

## 3. 功能需求

### 3.1 核心功能模块

#### 模块 1：学期管理
**功能描述**：管理学年学期信息，作为增值评价的时间维度

**用户故事**：
- 作为管理员，我需要创建和管理学年学期，以便将成绩数据关联到特定学期
- 作为教师，我需要查看当前学期和历史学期的数据

**主要功能**：
- 学期的 CRUD 操作
- 学期状态管理（进行中/已结束）
- 学期与年级的关联

**数据模型**：
```python
class Semester(Base):
    __tablename__ = "semesters"
    id = Column(Integer, primary_key=True)
    year = Column(String(20), nullable=False, comment="学年，如 2023-2024")
    term = Column(Integer, nullable=False, comment="学期：1或2")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
```

---

#### 模块 2：考试管理
**功能描述**：管理各类考试信息，包括期中、期末、入学考试等

**用户故事**：
- 作为教师，我需要创建考试并设置考试参数（满分、考试时间等）
- 作为管理员，我需要审核和发布考试安排
- 作为学生，我需要查看考试安排

**主要功能**：
- 考试的 CRUD 操作
- 考试类型管理（期中/期末/月考/入学考试）
- 考试与学科、年级、学期的关联
- 考试状态流转（计划中/进行中/已完成）

**数据模型**：
```python
class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    exam_type = Column(String(50), nullable=False)  # MIDTERM/FINAL/MONTHLY/ENTRANCE
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    grade_id = Column(Integer, ForeignKey("grades.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_score = Column(Float, default=100)
    status = Column(String(50), default="PLANNED")  # PLANNED/ONGOING/COMPLETED
    created_by = Column(Integer, ForeignKey("users.id"))
```

---

#### 模块 3：成绩管理
**功能描述**：记录和管理学生考试成绩

**用户故事**：
- 作为教师，我需要录入和导入学生成绩
- 作为系统，我需要自动计算标准分和百分位
- 作为学生，我需要查看我的历史成绩

**主要功能**：
- 成绩录入（单个/批量导入）
- 标准分自动计算（Z-score）
- 百分位计算
- 成绩发布与状态管理
- 成绩修改历史记录

**数据模型**：
```python
class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    raw_score = Column(Float, nullable=False, comment="原始分数")
    standard_score = Column(Float, comment="标准分（Z-score）")
    percentile = Column(Float, comment="百分位排名")
    grade = Column(String(10), comment="等级 A/B/C/D/F")
    teacher_id = Column(Integer, ForeignKey("users.id"), comment="任课教师")
    status = Column(String(50), default="DRAFT")  # DRAFT/CONFIRMED/PUBLISHED
    created_at = Column(DateTime, default=datetime.utcnow)
```

**计算逻辑**：
```python
# 标准分计算
standard_score = (raw_score - mean) / std_deviation

# 百分位计算
percentile = (students_below / total_students) * 100
```

---

#### 模块 4：评价指标管理
**功能描述**：定义和管理增值评价指标

**用户故事**：
- 作为管理员，我需要配置评价指标和权重
- 作为系统，我需要支持自定义评价公式

**主要功能**：
- 评价指标的 CRUD
- 指标类型管理（成长型/水平型）
- 权重配置
- 公式编辑器

**数据模型**：
```python
class EvaluationMetric(Base):
    __tablename__ = "evaluation_metrics"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, comment="指标名称")
    metric_type = Column(String(50), nullable=False)  # GROWTH/LEVEL
    weight = Column(Float, default=1.0, comment="权重")
    formula = Column(Text, comment="计算公式（JSON格式）")
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
```

**预置指标**：
1. **简单进步分**：`current_score - base_score`
2. **进步率**：`(current_score - base_score) / (max_score - base_score)`
3. **标准化增值**：`(current_z_score - base_z_score)`
4. **百分位提升**：`current_percentile - base_percentile`

---

#### 模块 5：增值评价计算引擎（核心）
**功能描述**：计算学生、教师、学校的增值分数

**用户故事**：
- 作为系统，我需要根据配置的指标自动计算增值
- 作为教师，我需要查看我的班级增值评价结果
- 作为管理员，我需要生成全校/全区域的增值报告

**主要功能**：
- 自动触发增值计算
- 支持多维度评价（学生/教师/班级/学校/区域）
- 影响因素调整（家庭背景、学校条件）
- 增值排名与对比
- 计算结果可视化

**数据模型**：
```python
class ValueAddedEvaluation(Base):
    __tablename__ = "value_added_evaluations"
    id = Column(Integer, primary_key=True)
    target_type = Column(String(50), nullable=False)  # STUDENT/TEACHER/CLASSROOM/SCHOOL/REGION
    target_id = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))
    base_score = Column(Float, comment="基期平均分")
    current_score = Column(Float, comment="现期平均分")
    added_value = Column(Float, nullable=False, comment="增值分数")
    confidence_interval = Column(JSON, comment="置信区间")
    factors = Column(JSON, comment="影响因素调整系数")
    rank_in_scope = Column(Integer, comment="排名")
    total_in_scope = Column(Integer, comment="总人数")
    status = Column(String(50), default="DRAFT")  # DRAFT/CONFIRMED/PUBLISHED
    calculated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
```

**计算公式示例**：

**教师增值评价**：
```python
# 1. 获取教师所教班级学生
students = get_students_by_teacher(teacher_id, subject_id, semester_id)

# 2. 计算基期平均分
base_scores = [get_score(student, base_exam) for student in students]
base_mean = mean(base_scores)

# 3. 计算现期平均分
current_scores = [get_score(student, current_exam) for student in students]
current_mean = mean(current_scores)

# 4. 计算增值（考虑预期进步）
expected_growth = get_expected_growth(grade_level, subject)
added_value = (current_mean - base_mean) - expected_growth

# 5. 多因素调整（可选）
factors = calculate_factors(students)  # 家庭背景、学校资源等
adjusted_value = added_value / factors
```

---

#### 模块 6：统计分析与报表
**功能描述**：生成各类增值评价报表和可视化图表

**用户故事**：
- 作为管理员，我需要生成学校增值排名报告
- 作为教师，我需要查看我班学生的进步分布
- 作为家长，我需要了解孩子的成长趋势

**主要功能**：
- 增值趋势图
- 学科对比分析
- 排行榜（教师/班级/学校）
- 导出报表（PDF/Excel）
- 数据仪表盘

**数据模型**：
```python
class StatisticalAnalysis(Base):
    __tablename__ = "statistical_analyses"
    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey("evaluation_metrics.id"))
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    period_start = Column(Date)
    period_end = Column(Date)
    result = Column(JSON, comment="分析结果数据")
    status = Column(String(50), default="PROCESSING")  # PROCESSING/COMPLETED/ERROR
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

### 3.2 可选功能模块（二期）

#### 模块 7：家庭背景管理
- 收集学生家庭信息
- 用于增值评价的因素调整

#### 模块 8：教师团队管理
- 教研组管理
- 团队增值评价

#### 模块 9：学生历史追踪
- 学生转班、转校记录
- 历史教师关联

---

## 4. API 设计

### 4.1 学期管理 API
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/semesters/` | 创建学期 |
| GET | `/api/v1/semesters/` | 获取学期列表 |
| GET | `/api/v1/semesters/{id}` | 获取学期详情 |
| PUT | `/api/v1/semesters/{id}` | 更新学期 |
| DELETE | `/api/v1/semesters/{id}` | 删除学期 |

### 4.2 考试管理 API
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/exams/` | 创建考试 |
| GET | `/api/v1/exams/` | 获取考试列表 |
| GET | `/api/v1/exams/{id}` | 获取考试详情 |
| PUT | `/api/v1/exams/{id}` | 更新考试 |
| DELETE | `/api/v1/exams/{id}` | 删除考试 |
| POST | `/api/v1/exams/{id}/publish` | 发布考试 |

### 4.3 成绩管理 API
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/scores/` | 录入单个成绩 |
| POST | `/api/v1/scores/bulk` | 批量导入成绩 |
| GET | `/api/v1/scores/` | 获取成绩列表 |
| GET | `/api/v1/students/{id}/scores` | 获取学生成绩历史 |
| PUT | `/api/v1/scores/{id}` | 更新成绩 |
| POST | `/api/v1/scores/{id}/confirm` | 确认成绩 |
| POST | `/api/v1/scores/calculate-stats` | 计算统计指标（标准分/百分位） |

### 4.4 增值评价 API
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/evaluations/calculate` | 触发增值计算 |
| GET | `/api/v1/evaluations/` | 获取评价结果列表 |
| GET | `/api/v1/evaluations/{id}` | 获取评价详情 |
| GET | `/api/v1/teachers/{id}/evaluation` | 获取教师增值评价 |
| GET | `/api/v1/students/{id}/evaluation` | 获取学生增值评价 |
| GET | `/api/v1/schools/{id}/evaluation` | 获取学校增值评价 |
| GET | `/api/v1/evaluations/rankings` | 获取增值排名 |

### 4.5 统计分析 API
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/analyses/` | 创建分析任务 |
| GET | `/api/v1/analyses/{id}` | 获取分析结果 |
| GET | `/api/v1/reports/evaluation` | 生成增值评价报告 |
| GET | `/api/v1/dashboard/evaluation` | 获取评价仪表盘数据 |

---

## 5. 前端页面设计

### 5.1 页面结构
```
/evaluation
├── /semesters          # 学期管理
├── /exams             # 考试管理
│   ├── /list          # 考试列表
│   ├── /create        # 创建考试
│   └── /:id           # 考试详情（含成绩录入）
├── /scores            # 成绩管理
│   ├── /my            # 我的成绩（学生视图）
│   ├── /class         # 班级成绩（教师视图）
│   └── /import        # 成绩导入
├── /evaluations       # 增值评价
│   ├── /dashboard     # 评价仪表盘
│   ├── /teacher       # 教师增值
│   ├── /student       # 学生成长
│   ├── /school        # 学校质量
│   └── /rankings      # 排行榜
└── /reports           # 报表中心
```

### 5.2 核心页面原型

#### 页面 1：评价仪表盘
**布局**：
- 顶部：学期选择器、学科筛选
- 左侧：评价对象切换（教师/班级/学校）
- 中间：
  - 增值分数卡片（当前值、排名）
  - 增值趋势图（折线图）
  - 学科对比雷达图
- 右侧：影响因素分析

#### 页面 2：教师增值评价详情
**内容**：
- 教师基本信息
- 所教班级列表
- 各学科增值分数
- 与同类教师对比
- 学生进步分布（箱线图）
- 历史趋势（折线图）

#### 页面 3：成绩录入
**功能**：
- 考试信息展示
- 学生名单表格
- 成绩输入框
- 自动保存
- 批量导入（Excel）
- 标准分实时预览

---

## 6. 技术实现要点

### 6.1 数据库迁移策略
1. **阶段一**：新增核心表（Semester, Exam, Score, EvaluationMetric, ValueAddedEvaluation）
2. **阶段二**：扩展现有模型（Classroom 增加 capacity 字段）
3. **阶段三**：可选功能表（Family, TeacherTeam 等）

### 6.2 数据初始化
```bash
# 创建迁移文件
alembic revision --autogenerate -m "add value added evaluation tables"

# 应用迁移
alembic upgrade head

# 初始化默认学期（Python脚本）
python scripts/init_semesters.py
```

### 6.3 性能优化
- 增值计算使用后台任务（Celery/BackgroundTasks）
- 成绩统计数据缓存（Redis）
- 大数据量查询优化（索引、分页）
- 定时任务预计算常用指标

### 6.4 权限控制
| 角色 | 权限 |
|------|------|
| Admin | 全部权限 |
| Researcher | 查看所有数据，导出报表 |
| Teacher | 查看自己班级/学生数据，录入成绩 |
| Student | 仅查看自己的成绩和成长数据 |

### 6.5 数据验证
- 成绩范围校验（0 ~ 满分）
- 考试时间逻辑校验（结束 > 开始）
- 增值计算前置条件检查（必须有基期和现期成绩）
- 数据完整性校验（学生必须属于班级、考试必须关联学科）

---

## 7. 实施计划

### 阶段一：基础数据模型（Week 1-2）
- [ ] 创建 Semester 模型和 API
- [ ] 创建 Exam 模型和 API
- [ ] 创建 Score 模型和 API
- [ ] 数据库迁移
- [ ] 单元测试

### 阶段二：成绩管理功能（Week 3-4）
- [ ] 成绩录入页面
- [ ] 成绩批量导入功能
- [ ] 标准分/百分位计算
- [ ] 成绩查询和展示

### 阶段三：增值评价核心（Week 5-7）
- [ ] 评价指标管理
- [ ] 增值计算引擎
- [ ] 评价结果存储
- [ ] 排名和对比功能

### 阶段四：可视化与报表（Week 8-9）
- [ ] 仪表盘页面
- [ ] 趋势图表组件
- [ ] 报表导出功能
- [ ] 数据对比分析

### 阶段五：测试与优化（Week 10）
- [ ] 集成测试
- [ ] 性能优化
- [ ] 用户验收测试
- [ ] 文档完善

---

## 8. 成功指标

### 8.1 功能指标
- 支持至少 3 种增值评价算法
- 计算响应时间 < 5 秒（1000 学生规模）
- 成绩导入支持 Excel/CSV 格式
- 报表导出支持 PDF/Excel 格式

### 8.2 质量指标
- 单元测试覆盖率 > 80%
- API 响应时间 < 500ms（P95）
- 数据准确性 100%

---

## 9. 风险与挑战

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 数据质量不足（历史成绩缺失） | 高 | 提供数据补录工具，分阶段实施 |
| 计算复杂度高 | 中 | 使用后台任务，增量计算 |
| 用户理解偏差（增值 vs 绝对分数） | 中 | 提供培训材料，可视化说明 |
| 权限与隐私问题 | 高 | 严格权限控制，数据脱敏 |

---

## 10. 参考资料

### 10.1 增值评价理论
- Tennessee Value-Added Assessment System (TVAAS)
- EVAAS (Education Value-Added Assessment System)
- 我国教育质量监测增值评价模型

### 10.2 技术文档
- SQLAlchemy 2.0 文档
- FastAPI 异步编程指南
- Vue3 + TypeScript 最佳实践

---

**文档版本**：v1.0
**创建日期**：2026-01-11
**维护者**：InspireEd 产品团队
