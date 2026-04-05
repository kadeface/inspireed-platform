"""
评价系统 Pydantic Schemas

包括：
- 学期管理（Semester）
- 考试管理（Exam, ExamSubject, ExamNumberMapping）
- 成绩管理（Score）
- 增值评价（ValueAddedEvaluation, EvaluationDetail）
- 日常表现成绩（DailyPerformanceScore）
- 高中总分评价（ExamTotalScore）
- 导入任务（ImportTask）
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# 枚举类型
# ============================================================================

class ExamTypeEnum(str, Enum):
    """考试类型"""
    MIDTERM = "midterm"           # 期中考试
    FINAL = "final"               # 期末考试
    MONTHLY = "monthly"           # 月考
    UNIT = "unit"                 # 单元测试
    MOCK = "mock"                 # 模拟考试
    DISTRICTUnified = "district_unified"  # 区县统考
    ENTRANCE = "entrance"         # 中考/高考


class ExamStatusEnum(str, Enum):
    """考试状态"""
    DRAFT = "draft"               # 草稿
    SCHEDULED = "scheduled"       # 已安排
    IN_PROGRESS = "in_progress"   # 进行中
    COMPLETED = "completed"       # 已完成
    CANCELLED = "cancelled"       # 已取消


class ExamLevelEnum(str, Enum):
    """考试级别"""
    SCHOOL = "school"             # 学校级考试
    DISTRICT = "district"         # 区县统考
    CITY = "city"                 # 市级考试


# 考试级别的字面量类型（用于验证）
EXAM_LEVEL_VALUES = {"school", "district", "city"}


class MetricTypeEnum(str, Enum):
    """指标类型"""
    RATE = "rate"                 # 率指标（优秀率、及格率等）
    AVERAGE = "average"           # 平均分
    COUNT = "count"               # 人数
    SCORE = "score"               # 分数


class MetricCategoryEnum(str, Enum):
    """指标分类"""
    EXCELLENCE = "excellence"     # 优秀类（优秀率、优良率）
    PASS = "pass"                 # 合格类（合格率、低分率）
    AVERAGE = "average"           # 平均类
    CUSTOM = "custom"             # 自定义


class ScopeTypeEnum(str, Enum):
    """评价范围类型"""
    REGION = "region"             # 区县级
    SCHOOL = "school"             # 学校级
    CLASSROOM = "classroom"       # 班级级


class ImportStatusEnum(str, Enum):
    """导入任务状态"""
    PENDING = "pending"           # 待处理
    PROCESSING = "processing"     # 处理中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败


# ============================================================================
# 学期管理（Semester）
# ============================================================================

class SemesterBase(BaseModel):
    """学期基础模型"""
    year: str = Field(..., description="学年，格式：2023-2024", pattern=r"^\d{4}-\d{4}$")
    semester_type: str = Field(..., description="学期类型：上学期/下学期")
    name: str = Field(..., description="学期名称", max_length=100)
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    is_current: bool = Field(default=False, description="是否为当前学期")
    region_id: Optional[int] = Field(None, description="区县ID（可选）")


class SemesterCreate(SemesterBase):
    """创建学期"""
    pass


class SemesterUpdate(BaseModel):
    """更新学期"""
    year: Optional[str] = Field(None, description="学年，格式：2023-2024", pattern=r"^\d{4}-\d{4}$")
    semester_type: Optional[str] = None
    name: Optional[str] = Field(None, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None
    region_id: Optional[int] = None


class SemesterResponse(SemesterBase):
    """学期响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# 考试管理（Exam, ExamSubject, ExamNumberMapping）
# ============================================================================

class ExamBase(BaseModel):
    """考试基础模型"""
    name: str = Field(..., description="考试名称", max_length=200)
    exam_type: ExamTypeEnum = Field(..., description="考试类型")
    exam_level: str = Field(default="school", description="考试级别：school/district/city")
    exam_date: datetime = Field(..., description="考试日期")
    semester_id: int = Field(..., description="学期ID")
    grade_id: int = Field(..., description="年级ID")
    region_id: Optional[int] = Field(None, description="区县ID")
    school_id: Optional[int] = Field(None, description="学校ID")
    status: ExamStatusEnum = Field(default=ExamStatusEnum.DRAFT, description="考试状态")
    statistics: Optional[Dict[str, Any]] = Field(None, description="考试统计信息（JSON）")

    @field_validator('exam_level')
    @classmethod
    def validate_exam_level(cls, v: str) -> str:
        """验证考试级别"""
        if v not in EXAM_LEVEL_VALUES:
            raise ValueError(f"exam_level 必须是以下值之一: {EXAM_LEVEL_VALUES}")
        return v


class ExamCreate(ExamBase):
    """创建考试"""
    pass


class ExamUpdate(BaseModel):
    """更新考试"""
    name: Optional[str] = Field(None, max_length=200)
    exam_type: Optional[ExamTypeEnum] = None
    exam_level: Optional[ExamLevelEnum] = None
    exam_date: Optional[datetime] = None
    semester_id: Optional[int] = None
    grade_id: Optional[int] = None
    region_id: Optional[int] = None
    school_id: Optional[int] = None
    status: Optional[ExamStatusEnum] = None
    statistics: Optional[Dict[str, Any]] = None


class ExamResponse(ExamBase):
    """考试响应"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExamSubjectBase(BaseModel):
    """考试科目关联基础模型"""
    exam_id: int = Field(..., description="考试ID")
    subject_id: int = Field(..., description="科目ID")
    full_score: int = Field(..., description="满分", ge=0, le=150)
    pass_line: Optional[int] = Field(None, description="及格线")
    excellent_line: Optional[int] = Field(None, description="优秀线")
    good_line: Optional[int] = Field(None, description="良好线")


class ExamSubjectCreate(ExamSubjectBase):
    """创建考试科目关联"""
    pass


class ExamSubjectUpdate(BaseModel):
    """更新考试科目关联"""
    full_score: Optional[int] = Field(None, ge=0, le=150)
    pass_line: Optional[int] = None
    excellent_line: Optional[int] = None
    good_line: Optional[int] = None


class ExamSubjectResponse(ExamSubjectBase):
    """考试科目关联响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# 成绩管理（Score）
# ============================================================================

class ScoreBase(BaseModel):
    """成绩基础模型"""
    exam_id: int = Field(..., description="考试ID")
    subject_id: int = Field(..., description="科目ID")
    student_id: int = Field(..., description="学生ID")
    raw_score: float = Field(..., description="原始分", ge=0, le=150)
    is_absent: bool = Field(default=False, description="是否缺考")
    is_cheated: bool = Field(default=False, description="是否作弊")


class ScoreCreate(ScoreBase):
    """创建成绩"""
    pass


class ScoreUpdate(BaseModel):
    """更新成绩"""
    raw_score: Optional[float] = Field(None, ge=0, le=150)
    is_absent: Optional[bool] = None
    is_cheated: Optional[bool] = None


class ScoreResponse(ScoreBase):
    """成绩响应"""
    id: int
    standard_score: Optional[float] = Field(None, description="标准分")
    percentile: Optional[float] = Field(None, description="百分位")
    grade_level: Optional[str] = Field(None, description="等级")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# 增值评价（ValueAddedEvaluation, EvaluationDetail）
# ============================================================================

class ValueAddedEvaluationBase(BaseModel):
    """增值评价基础模型"""
    name: str = Field(..., description="评价名称", max_length=200)
    scope_type: ScopeTypeEnum = Field(..., description="评价范围类型")
    scope_id: int = Field(..., description="评价范围ID（区县/学校/班级ID）")
    baseline_exam_id: int = Field(..., description="基线考试ID")
    endline_exam_id: int = Field(..., description="结束考试ID")
    subject_id: Optional[int] = Field(None, description="科目ID（可选，为空则计算总分）")


class ValueAddedEvaluationCreate(ValueAddedEvaluationBase):
    """创建增值评价"""
    region_id: Optional[int] = Field(None, description="区县ID")
    school_id: Optional[int] = Field(None, description="学校ID")
    classroom_id: Optional[int] = Field(None, description="班级ID")
    metrics: Optional[List[str]] = Field(None, description="指标列表")
    score_lines: Optional[Dict[str, float]] = Field(None, description="分数线配置")


class ValueAddedEvaluationUpdate(BaseModel):
    """更新增值评价"""
    name: Optional[str] = Field(None, max_length=200)
    scope_type: Optional[ScopeTypeEnum] = None
    scope_id: Optional[int] = None


class ValueAddedEvaluationResponse(ValueAddedEvaluationBase):
    """增值评价响应"""
    id: int
    baseline_value: Optional[float] = Field(None, description="基线值")
    endline_value: Optional[float] = Field(None, description="结束值")
    value_added: Optional[float] = Field(None, description="增值")
    value_added_rate: Optional[float] = Field(None, description="增值率")
    is_significant: bool = Field(default=False, description="是否显著")
    p_value: Optional[float] = Field(None, description="显著性水平P值")
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ValueAddedEvaluationSummary(BaseModel):
    """增值评价汇总"""
    evaluation_id: int
    name: str
    scope_type: str
    scope_id: Optional[int]
    baseline_exam: Dict[str, Any]
    endline_exam: Dict[str, Any]
    subject: Dict[str, Any]
    metrics: List[Dict[str, Any]]
    created_at: Optional[str]


# ============================================================================
# 日常表现成绩（DailyPerformanceScore）
# ============================================================================

class DailyPerformanceScoreBase(BaseModel):
    """日常表现成绩基础模型"""
    student_id: int = Field(..., description="学生ID")
    classroom_id: int = Field(..., description="班级ID")
    semester_id: Optional[int] = Field(None, description="学期ID（可选）")
    period_name: str = Field(..., description="统计周期名称", max_length=100)
    start_date: datetime = Field(..., description="统计开始日期")
    end_date: datetime = Field(..., description="统计结束日期")

    # 原始数据统计
    positive_behavior_count: int = Field(default=0, description="正面行为次数", ge=0)
    positive_behavior_points: int = Field(default=0, description="正面行为总积分", ge=0)
    discipline_count: int = Field(default=0, description="违纪次数", ge=0)
    discipline_points: int = Field(default=0, description="违纪扣分", ge=0)
    attendance_present_count: int = Field(default=0, description="出勤次数", ge=0)
    attendance_late_count: int = Field(default=0, description="迟到次数", ge=0)
    attendance_leave_count: int = Field(default=0, description="请假次数", ge=0)
    attendance_absent_count: int = Field(default=0, description="缺勤次数", ge=0)
    duty_completed_count: int = Field(default=0, description="值日完成次数", ge=0)

    # 百分制成绩
    final_score: float = Field(..., description="最终百分制成绩", ge=0, le=100)
    grade_level: str = Field(..., description="等级：优秀/良好/合格/不合格")

    # 详细分类得分（JSON）
    detail_scores: Optional[Dict[str, Any]] = Field(None, description="各分类详细得分和权重")

    # 备注
    note: Optional[str] = Field(None, description="教师评语或备注")


class DailyPerformanceScoreCreate(DailyPerformanceScoreBase):
    """创建日常表现成绩"""
    created_by: int = Field(..., description="创建人ID")


class DailyPerformanceScoreUpdate(BaseModel):
    """更新日常表现成绩"""
    final_score: Optional[float] = Field(None, ge=0, le=100)
    grade_level: Optional[str] = None
    detail_scores: Optional[Dict[str, Any]] = None
    note: Optional[str] = None


class DailyPerformanceScoreResponse(DailyPerformanceScoreBase):
    """日常表现成绩响应"""
    id: int
    created_by: int
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyPerformanceScoreCalculate(BaseModel):
    """计算日常表现成绩请求"""
    student_id: int = Field(..., description="学生ID")
    classroom_id: int = Field(..., description="班级ID")
    start_date: datetime = Field(..., description="统计开始日期")
    end_date: datetime = Field(..., description="统计结束日期")
    period_name: str = Field(..., description="统计周期名称", max_length=100)
    semester_id: Optional[int] = Field(None, description="学期ID（可选）")
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="自定义权重（可选）",
        json_schema_extra={
            "example": {
                "attendance": 0.20,
                "behavior": 0.40,
                "discipline": 0.30,
                "duty": 0.10
            }
        }
    )


class DailyPerformanceScoreBatchCalculate(BaseModel):
    """批量计算班级日常表现成绩请求"""
    classroom_id: int = Field(..., description="班级ID")
    start_date: datetime = Field(..., description="统计开始日期")
    end_date: datetime = Field(..., description="统计结束日期")
    period_name: str = Field(..., description="统计周期名称", max_length=100)
    semester_id: Optional[int] = Field(None, description="学期ID（可选）")
    weights: Optional[Dict[str, float]] = Field(None, description="自定义权重（可选）")


# ============================================================================
# 高中总分评价（ExamTotalScore）
# ============================================================================

class ExamTotalScoreBase(BaseModel):
    """高中总分评价基础模型"""
    exam_id: int = Field(..., description="考试ID")
    student_id: int = Field(..., description="学生ID")
    student_type: str = Field(..., description="学生类型：none/arts/science")
    total_score: int = Field(..., description="总分", ge=0, le=750)

    # 4条分数线
    c9_line: Optional[int] = Field(None, description="C9线（顶尖大学）", ge=0, le=750)
    special_control_line: Optional[int] = Field(None, description="特控线（一本线）", ge=0, le=750)
    undergraduate_line: Optional[int] = Field(None, description="本科线", ge=0, le=750)
    junior_college_line: Optional[int] = Field(None, description="专科线", ge=0, le=750)


class ExamTotalScoreCreate(ExamTotalScoreBase):
    """创建高中总分评价"""
    created_by: int = Field(..., description="创建人ID")


class ExamTotalScoreUpdate(BaseModel):
    """更新高中总分评价"""
    total_score: Optional[int] = Field(None, ge=0, le=750)
    student_type: Optional[str] = None
    c9_line: Optional[int] = Field(None, ge=0, le=750)
    special_control_line: Optional[int] = Field(None, ge=0, le=750)
    undergraduate_line: Optional[int] = Field(None, ge=0, le=750)
    junior_college_line: Optional[int] = Field(None, ge=0, le=750)


class ExamTotalScoreResponse(ExamTotalScoreBase):
    """高中总分评价响应"""
    id: int
    reached_c9: bool = Field(default=False, description="是否达到C9线")
    reached_special_control: bool = Field(default=False, description="是否达到特控线")
    reached_undergraduate: bool = Field(default=False, description="是否达到本科线")
    reached_junior_college: bool = Field(default=False, description="是否达到专科线")
    created_by: int
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExamTotalScoreBatchCreate(BaseModel):
    """批量创建高中总分评价请求"""
    exam_id: int = Field(..., description="考试ID")
    scores: list = Field(..., description="成绩数据列表", json_schema_extra={
        "example": [
            {
                "student_id": 1,
                "total_score": 680,
                "student_type": "science"
            }
        ]
    })


# ============================================================================
# 导入任务（ImportTask）
# ============================================================================

class ImportTaskBase(BaseModel):
    """导入任务基础模型"""
    task_name: str = Field(..., description="任务名称", max_length=200)
    task_type: str = Field(..., description="任务类型", max_length=50)
    exam_id: int = Field(..., description="考试ID")


class ImportTaskCreate(ImportTaskBase):
    """创建导入任务"""
    file_url: str = Field(..., description="文件URL")
    file_name: str = Field(..., description="文件名", max_length=255)
    file_size: int = Field(..., description="文件大小（字节）", ge=0)


class ImportTaskUpdate(BaseModel):
    """更新导入任务"""
    status: Optional[ImportStatusEnum] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    total_rows: Optional[int] = Field(None, ge=0)
    processed_rows: Optional[int] = Field(None, ge=0)
    failed_rows: Optional[int] = Field(None, ge=0)
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


class ImportTaskResponse(ImportTaskBase):
    """导入任务响应"""
    id: int
    file_url: str
    file_name: str
    file_size: int
    status: ImportStatusEnum
    progress: float = 0.0
    total_rows: Optional[int] = None
    processed_rows: Optional[int] = None
    failed_rows: Optional[int] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    created_by: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Alias for compatibility (ImportTaskResponse already includes progress)
ImportTaskWithProgressResponse = ImportTaskResponse


# ============================================================================
# 质量监测报告（MonitoringReport, MonitoringReportSchool）
# ============================================================================

class MonitoringReportResponse(BaseModel):
    """质量监测报告响应"""
    id: int
    name: str
    report_type: str
    academic_year: str
    semester_type: str
    region_id: Optional[int]
    source_file: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MonitoringReportSchoolResponse(BaseModel):
    """质量监测报告学校明细响应"""
    id: int
    report_id: int
    school_code: Optional[str]
    school_id: Optional[int]
    school_name: str
    display_order: int
    remarks: Optional[str]
    # 初中
    g9_one_point: Optional[float] = None
    g9_excellent_rate: Optional[float] = None
    g9_good_rate: Optional[float] = None
    g9_pass_rate: Optional[float] = None
    g9_low_rate: Optional[float] = None
    g9_comprehensive: Optional[float] = None
    g9_score: Optional[float] = None
    g9_rank: Optional[int] = None
    g8_one_point: Optional[float] = None
    g8_excellent_rate: Optional[float] = None
    g8_good_rate: Optional[float] = None
    g8_pass_rate: Optional[float] = None
    g8_low_rate: Optional[float] = None
    g8_comprehensive: Optional[float] = None
    g8_score: Optional[float] = None
    g8_rank: Optional[int] = None
    g7_one_point: Optional[float] = None
    g7_excellent_rate: Optional[float] = None
    g7_good_rate: Optional[float] = None
    g7_pass_rate: Optional[float] = None
    g7_low_rate: Optional[float] = None
    g7_comprehensive: Optional[float] = None
    g7_score: Optional[float] = None
    g7_rank: Optional[int] = None
    g789_one_point: Optional[float] = None
    g789_excellent_rate: Optional[float] = None
    g789_good_rate: Optional[float] = None
    g789_pass_rate: Optional[float] = None
    g789_low_rate: Optional[float] = None
    g789_total_score: Optional[float] = None
    g789_rank: Optional[int] = None
    g9_value_added_score: Optional[float] = None
    g9_value_added_rank: Optional[int] = None
    g8_value_added_score: Optional[float] = None
    g8_value_added_rank: Optional[int] = None
    g7_value_added_score: Optional[float] = None
    g7_value_added_rank: Optional[int] = None
    g789_value_added_score: Optional[float] = None
    g789_value_added_rank: Optional[int] = None
    # 小学
    g6_one_point: Optional[float] = None
    g6_excellent_rate: Optional[float] = None
    g6_good_rate: Optional[float] = None
    g6_pass_rate: Optional[float] = None
    g6_comprehensive: Optional[float] = None
    g6_score: Optional[float] = None
    g6_rank: Optional[int] = None
    g5_one_point: Optional[float] = None
    g5_excellent_rate: Optional[float] = None
    g5_good_rate: Optional[float] = None
    g5_pass_rate: Optional[float] = None
    g5_comprehensive: Optional[float] = None
    g5_score: Optional[float] = None
    g5_rank: Optional[int] = None
    g4_one_point: Optional[float] = None
    g4_excellent_rate: Optional[float] = None
    g4_good_rate: Optional[float] = None
    g4_pass_rate: Optional[float] = None
    g4_comprehensive: Optional[float] = None
    g4_score: Optional[float] = None
    g4_rank: Optional[int] = None
    g456_one_point: Optional[float] = None
    g456_excellent_rate: Optional[float] = None
    g456_good_rate: Optional[float] = None
    g456_pass_rate: Optional[float] = None
    g456_total_score: Optional[float] = None
    g456_rank: Optional[int] = None
    g6_value_added_score: Optional[float] = None
    g6_value_added_rank: Optional[int] = None
    g5_value_added_score: Optional[float] = None
    g5_value_added_rank: Optional[int] = None
    g4_value_added_score: Optional[float] = None
    g4_value_added_rank: Optional[int] = None
    g456_value_added_score: Optional[float] = None
    g456_value_added_rank: Optional[int] = None

    class Config:
        from_attributes = True


class MonitoringReportDetailResponse(MonitoringReportResponse):
    """质量监测报告详情（含学校明细）"""
    school_rows: List[MonitoringReportSchoolResponse] = []
