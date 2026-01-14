"""
增值评价系统模型

包含9个核心表：
1. Semester - 学期
2. Exam - 考试
3. ExamSubject - 考试科目关联
4. ExamNumberMapping - 考号映射
5. Score - 成绩
6. EvaluationMetric - 评价指标
7. ValueAddedEvaluation - 增值评价结果
8. EvaluationDetail - 评价明细
9. ImportTask - 导入任务
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Index,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ==================== 枚举定义 ====================

class ExamType(str, Enum):
    """考试类型枚举"""
    MIDTERM = "midterm"              # 期中考试
    FINAL = "final"                  # 期末考试
    MONTHLY = "monthly"              # 月考
    UNIT = "unit"                    # 单元测试
    MOCK = "mock"                    # 模拟考试
    DISTRICT_UNIFIED = "district_unified"  # 区县统考


class ExamStatus(str, Enum):
    """考试状态枚举"""
    DRAFT = "draft"                  # 草稿
    PUBLISHED = "published"          # 已发布
    IN_PROGRESS = "in_progress"      # 进行中
    COMPLETED = "completed"          # 已完成
    CANCELLED = "cancelled"          # 已取消


class MetricType(str, Enum):
    """指标类型枚举"""
    GROWTH = "growth"                # 成长型指标（增值）
    LEVEL = "level"                  # 水平型指标（绝对水平）
    RATE = "rate"                    # 率指标（百分比）


class MetricCategory(str, Enum):
    """指标分类枚举"""
    EXCELLENCE_RATE = "excellence_rate"  # 优秀率
    GOOD_RATE = "good_rate"              # 优良率
    PASS_RATE = "pass_rate"              # 合格率
    LOW_RATE = "low_rate"                # 低分率
    AVERAGE_SCORE = "average_score"      # 平均分
    TOTAL_SCORE = "total_score"          # 总分


class ImportStatus(str, Enum):
    """导入任务状态枚举"""
    PENDING = "pending"              # 待处理
    PROCESSING = "processing"        # 处理中
    COMPLETED = "completed"          # 已完成
    FAILED = "failed"                # 失败
    CANCELLED = "cancelled"          # 已取消


# ==================== 模型定义 ====================

class Semester(Base):
    """学期模型"""
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String(20), nullable=False, comment="学年，格式：2023-2024")
    semester_type = Column(String(20), nullable=False, comment="学期类型：up/down")
    name = Column(String(50), nullable=False, comment="学期名称，如2024-2025学年上学期")
    start_date = Column(DateTime, nullable=False, comment="学期开始日期")
    end_date = Column(DateTime, nullable=False, comment="学期结束日期")
    is_current = Column(Boolean, default=False, comment="是否当前学期")

    # 关联区县（可选，用于区县级别学期）
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, comment="区县ID")

    # 标准字段
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    region = relationship("Region", foreign_keys=[region_id])
    exams = relationship("Exam", back_populates="semester")

    # 约束
    __table_args__ = (
        UniqueConstraint('year', 'semester_type', 'region_id', name='uq_semester_year_region'),
    )


class Exam(Base):
    """考试模型"""
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="考试名称")
    exam_type = Column(
        SQLEnum(ExamType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment="考试类型"
    )
    status = Column(
        SQLEnum(ExamStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        default=ExamStatus.DRAFT,
        comment="考试状态"
    )

    # 关联
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False, comment="年级ID")
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, comment="区县ID（统考必填）")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True, comment="学校ID（校级考试）")

    # 时间信息
    exam_date = Column(DateTime, nullable=False, comment="考试日期")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 统计信息（JSON格式，存储考试统计结果）
    statistics = Column(JSON, nullable=True, comment="考试统计结果")

    # 标准字段
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    semester = relationship("Semester", back_populates="exams")
    grade = relationship("Grade")
    region = relationship("Region", foreign_keys=[region_id])
    school = relationship("School", foreign_keys=[school_id])
    creator = relationship("User", foreign_keys=[created_by])
    exam_subjects = relationship("ExamSubject", back_populates="exam", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="exam", cascade="all, delete-orphan")
    exam_number_mappings = relationship("ExamNumberMapping", back_populates="exam", cascade="all, delete-orphan")


class ExamSubject(Base):
    """考试科目关联表（多对多）"""
    __tablename__ = "exam_subjects"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    # 该科目在此次考试中的配置
    full_score = Column(Integer, nullable=False, default=100, comment="满分")
    pass_line = Column(Integer, nullable=False, default=60, comment="及格线")
    excellent_line = Column(Integer, nullable=False, default=85, comment="优秀线")
    good_line = Column(Integer, nullable=False, default=75, comment="良好线")

    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    exam = relationship("Exam", back_populates="exam_subjects")
    subject = relationship("Subject")

    # 约束
    __table_args__ = (
        UniqueConstraint('exam_id', 'subject_id', name='uq_exam_subject'),
    )


class ExamNumberMapping(Base):
    """考号映射表（支持跨学年追踪）"""
    __tablename__ = "exam_number_mappings"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_number = Column(String(50), nullable=False, comment="考号（准考证号）")

    # 冗余字段，加速查询
    student_id_number = Column(String(50), nullable=False, comment="学籍号/身份证号")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, comment="学校ID")
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, comment="班级ID")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    exam = relationship("Exam", back_populates="exam_number_mappings")
    student = relationship("User")
    school = relationship("School")
    classroom = relationship("Classroom")

    # 约束和索引
    __table_args__ = (
        UniqueConstraint('exam_id', 'exam_number', name='uq_exam_number'),
        Index('idx_exam_student_mapping', 'exam_id', 'student_id'),
    )


class Score(Base):
    """成绩表（窄字段设计）"""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 原始分
    raw_score = Column(Integer, nullable=False, comment="原始分")

    # 标准分（可选，用于跨考试比较）
    standard_score = Column(Float, nullable=True, comment="标准分")

    # 百分位（可选）
    percentile = Column(Float, nullable=True, comment="百分位排名（0-100）")

    # 等级（可选，根据分数线自动计算）
    grade_level = Column(String(20), nullable=True, comment="等级：优秀/良好/合格/不合格")

    # 元数据
    is_absent = Column(Boolean, default=False, comment="是否缺考")
    is_cheated = Column(Boolean, default=False, comment="是否作弊")

    # 标准字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    exam = relationship("Exam", back_populates="scores")
    subject = relationship("Subject")
    student = relationship("User")

    # 约束和索引
    __table_args__ = (
        UniqueConstraint('exam_id', 'subject_id', 'student_id', name='uq_exam_subject_student'),
        Index('idx_exam_subject_score', 'exam_id', 'subject_id'),
        Index('idx_student_scores', 'student_id'),
    )


class ExamTotalScore(Base):
    """总分评价表

    用于存储学生的总分成绩和等级评价，主要用于：
    - 高中总分评价（高考、模考）
    - 支持文理科区分和不同的分数线体系（C9线、特控线、本科线、专科线）

    注意：
    - 高一第一学期等未分科阶段，student_type 为 'none'
    - 文理科分科后，student_type 为 'arts' 或 'science'
    - 分科时间因地区和学校而异
    """

    __tablename__ = "exam_total_scores"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 文理科标识（从 User.student_type 继承，冗余存储便于查询）
    student_type = Column(
        SQLEnum(
            "StudentType",
            native_enum=False,
            values_callable=lambda enum_cls: ["none", "arts", "science"],
        ),
        nullable=False,
        comment="学生类型：none(未分科，含小学/初中/高中未分科阶段)/arts(文科)/science(理科)",
    )

    # 总分
    total_score = Column(Integer, nullable=False, comment="考试总分（主要用于高考）")

    # 高中分数线（根据文理科自动选择）
    c9_line = Column(Integer, nullable=True, comment="C9线（顶尖大学）")
    special_control_line = Column(Integer, nullable=True, comment="特控线（特殊控制线/一本线）")
    undergraduate_line = Column(Integer, nullable=True, comment="本科线")
    junior_college_line = Column(Integer, nullable=True, comment="专科线")

    # 达标情况（自动计算）
    reached_c9 = Column(Boolean, default=False, comment="是否达到C9线")
    reached_special_control = Column(Boolean, default=False, comment="是否达到特控线")
    reached_undergraduate = Column(Boolean, default=False, comment="是否达到本科线")
    reached_junior_college = Column(Boolean, default=False, comment="是否达到专科线")

    # 元数据
    is_absent = Column(Boolean, default=False, comment="是否缺考")
    is_cheated = Column(Boolean, default=False, comment="是否作弊")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    exam = relationship("Exam")
    student = relationship("User")

    # 约束和索引
    __table_args__ = (
        UniqueConstraint('exam_id', 'student_id', name='uq_exam_student_total'),
        Index('idx_exam_total_scores', 'exam_id'),
        Index('idx_student_total_scores', 'student_id'),
        Index('idx_student_type', 'student_type'),
    )


class DailyPerformanceScore(Base):
    """日常表现成绩表

    用于记录和统计学生的日常表现成绩，包括考勤、课堂表现、纪律、值日等。
    采用百分制（0-100分），与考试分数体系一致，但独立于增值评价系统。

    计算逻辑：
    1. 正面行为积分（PositiveBehavior.points）
    2. 纪律扣分（DisciplineRecord，每次扣分）
    3. 考勤记录（AttendanceEntry，缺勤扣分）
    4. 值日完成情况（DutyAssignment，完成加分）
    5. 综合计算转换为0-100分

    统计周期灵活：可按学期/月/考试周期等配置
    """

    __tablename__ = "daily_performance_scores"

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="学生ID")
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, comment="班级ID")
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=True, comment="学期ID（可选）")

    # 统计时间范围（灵活配置）
    period_name = Column(String(100), nullable=False, comment="统计周期名称，如'2024年上学期'/'2024年3月'/'第一次月考前'")
    start_date = Column(DateTime, nullable=False, comment="统计开始日期")
    end_date = Column(DateTime, nullable=False, comment="统计结束日期")

    # 原始数据统计
    positive_behavior_count = Column(Integer, default=0, nullable=False, comment="正面行为次数")
    positive_behavior_points = Column(Integer, default=0, nullable=False, comment="正面行为总积分")
    discipline_count = Column(Integer, default=0, nullable=False, comment="违纪次数")
    discipline_points = Column(Integer, default=0, nullable=False, comment="违纪扣分")
    attendance_present_count = Column(Integer, default=0, nullable=False, comment="出勤次数")
    attendance_late_count = Column(Integer, default=0, nullable=False, comment="迟到次数")
    attendance_leave_count = Column(Integer, default=0, nullable=False, comment="请假次数")
    attendance_absent_count = Column(Integer, default=0, nullable=False, comment="缺勤次数")
    duty_completed_count = Column(Integer, default=0, nullable=False, comment="值日完成次数")

    # 转换后的百分制成绩（0-100）
    final_score = Column(Float, nullable=False, comment="最终百分制成绩")
    grade_level = Column(String(20), nullable=True, comment="等级：优秀/良好/合格/不合格")

    # 详细分类得分（JSON格式，可选）
    detail_scores = Column(JSON, nullable=True, comment="""
    各分类详细得分：
    {
        "attendance_score": 95,      # 考勤得分
        "behavior_score": 88,        # 课堂表现得分
        "discipline_score": 90,      # 纪律得分
        "duty_score": 100,           # 值日得分
        "attendance_weight": 0.2,    # 考勤权重
        "behavior_weight": 0.4,      # 表现权重
        "discipline_weight": 0.3,    # 纪律权重
        "duty_weight": 0.1           # 值日权重
    }
    """)

    # 备注
    note = Column(Text, nullable=True, comment="教师评语或备注")

    # 元数据
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建人ID")
    calculated_at = Column(DateTime, nullable=False, comment="计算时间")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    student = relationship("User", foreign_keys=[student_id])
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    semester = relationship("Semester", foreign_keys=[semester_id])
    creator = relationship("User", foreign_keys=[created_by])

    # 索引
    __table_args__ = (
        Index('idx_daily_performance_student', 'student_id'),
        Index('idx_daily_performance_classroom', 'classroom_id'),
        Index('idx_daily_performance_period', 'start_date', 'end_date'),
        Index('idx_daily_performance_semester', 'semester_id'),
    )


class EvaluationMetric(Base):
    """评价指标定义"""
    __tablename__ = "evaluation_metrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="指标名称")
    code = Column(String(50), nullable=False, unique=True, comment="指标代码")
    description = Column(Text, nullable=True, comment="指标说明")

    metric_type = Column(
        SQLEnum(MetricType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment="指标类型"
    )
    metric_category = Column(
        SQLEnum(MetricCategory, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment="指标分类"
    )

    # 计算配置（JSON格式，存储计算公式、参数等）
    calculation_config = Column(JSON, nullable=True, comment="计算配置")

    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ValueAddedEvaluation(Base):
    """增值评价结果（首尾对比模型）"""
    __tablename__ = "value_added_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="评价名称")

    # 评价范围
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, comment="区县ID")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True, comment="学校ID")
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True, comment="班级ID")
    scope_type = Column(String(20), nullable=False, comment="评价范围类型：region/school/classroom")

    # 首尾考试关联
    baseline_exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, comment="基线考试（起始）ID")
    endline_exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, comment="结束考试（末次）ID")

    # 科目
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, comment="科目ID")

    # 评价结果
    baseline_value = Column(Float, nullable=False, comment="基线值")
    endline_value = Column(Float, nullable=False, comment="结束值")
    value_added = Column(Float, nullable=False, comment="增值量（endline - baseline）")
    value_added_rate = Column(Float, nullable=False, comment="增值率（百分比）")

    # 统计显著性
    is_significant = Column(Boolean, nullable=True, comment="是否显著")
    p_value = Column(Float, nullable=True, comment="p值")

    # 元数据
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    region = relationship("Region", foreign_keys=[region_id])
    school = relationship("School", foreign_keys=[school_id])
    classroom = relationship("Classroom", foreign_keys=[classroom_id])
    baseline_exam = relationship("Exam", foreign_keys=[baseline_exam_id])
    endline_exam = relationship("Exam", foreign_keys=[endline_exam_id])
    subject = relationship("Subject")
    creator = relationship("User", foreign_keys=[created_by])
    details = relationship("EvaluationDetail", back_populates="evaluation", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_evaluation_scope', 'scope_type', 'region_id', 'school_id', 'classroom_id'),
        Index('idx_evaluation_exams', 'baseline_exam_id', 'endline_exam_id'),
        Index('idx_evaluation_subject', 'subject_id'),
    )


class EvaluationDetail(Base):
    """评价明细表（存储率指标详细记录）"""
    __tablename__ = "evaluation_details"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("value_added_evaluations.id", ondelete="CASCADE"), nullable=False)
    metric_id = Column(Integer, ForeignKey("evaluation_metrics.id"), nullable=False)

    # 分层数据
    scope_type = Column(String(20), nullable=False, comment="层级：region/school/classroom")
    scope_id = Column(Integer, nullable=True, comment="层级ID")

    # 基线值和结束值
    baseline_count = Column(Integer, nullable=False, comment="基线分子数")
    baseline_total = Column(Integer, nullable=False, comment="基线分母数")
    baseline_rate = Column(Float, nullable=False, comment="基线率")

    endline_count = Column(Integer, nullable=False, comment="结束分子数")
    endline_total = Column(Integer, nullable=False, comment="结束分母数")
    endline_rate = Column(Float, nullable=False, comment="结束率")

    # 增值
    value_added = Column(Float, nullable=False, comment="增值量（百分点）")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    evaluation = relationship("ValueAddedEvaluation", back_populates="details")
    metric = relationship("EvaluationMetric")

    # 约束
    __table_args__ = (
        UniqueConstraint('evaluation_id', 'metric_id', 'scope_type', 'scope_id', name='uq_evaluation_metric_scope'),
    )


class ImportTask(Base):
    """导入任务表（异步导入）"""
    __tablename__ = "import_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(200), nullable=False, comment="任务名称")
    task_type = Column(String(50), nullable=False, comment="导入类型：exam_data/score_data")

    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True, comment="关联考试ID")

    # 文件信息
    file_url = Column(String(500), nullable=False, comment="上传文件URL")
    file_name = Column(String(200), nullable=False, comment="原始文件名")
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")

    # 进度信息
    status = Column(
        SQLEnum(ImportStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        default=ImportStatus.PENDING,
        comment="任务状态"
    )
    progress = Column(Integer, default=0, comment="进度百分比（0-100）")
    total_rows = Column(Integer, nullable=True, comment="总行数")
    processed_rows = Column(Integer, default=0, comment="已处理行数")
    failed_rows = Column(Integer, default=0, comment="失败行数")

    # 错误信息
    error_message = Column(Text, nullable=True, comment="错误信息")
    error_details = Column(JSON, nullable=True, comment="详细错误信息（JSON）")

    # 操作人
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 时间信息
    started_at = Column(DateTime, nullable=True, comment="开始处理时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    exam = relationship("Exam")
    creator = relationship("User")
