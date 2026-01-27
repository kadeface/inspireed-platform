"""
教师教学任务相关 Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================

class TeachingAssignmentTypeEnum(str, Enum):
    """教学任务类型枚举"""
    HEAD_TEACHER = "head_teacher"          # 班主任
    SUBJECT_TEACHER = "subject_teacher"    # 学科教师


# ============================================================================
# 基础模型
# ============================================================================

class TeacherTeachingAssignmentBase(BaseModel):
    """教师教学任务基础模型"""
    
    teacher_id: int = Field(..., description="教师ID")
    school_id: int = Field(..., description="学校ID")
    grade_id: int = Field(..., description="年级ID")
    classroom_id: int = Field(..., description="班级ID")
    subject_id: int = Field(..., description="学科ID")
    semester_id: int = Field(..., description="学期ID")
    academic_year: str = Field(..., max_length=20, description="学年，如 2023-2024")
    assignment_type: Optional[TeachingAssignmentTypeEnum] = Field(None, description="任务类型（已废弃，保留用于向后兼容）：HEAD_TEACHER(班主任)/SUBJECT_TEACHER(学科教师)")
    is_active: bool = Field(True, description="是否激活")


# ============================================================================
# 请求模型
# ============================================================================

class TeacherTeachingAssignmentCreate(TeacherTeachingAssignmentBase):
    """创建教师教学任务请求"""
    pass


class TeacherTeachingAssignmentUpdate(BaseModel):
    """更新教师教学任务请求"""
    
    teacher_id: Optional[int] = Field(None, description="教师ID")
    school_id: Optional[int] = Field(None, description="学校ID")
    grade_id: Optional[int] = Field(None, description="年级ID")
    classroom_id: Optional[int] = Field(None, description="班级ID")
    subject_id: Optional[int] = Field(None, description="学科ID")
    semester_id: Optional[int] = Field(None, description="学期ID")
    academic_year: Optional[str] = Field(None, max_length=20, description="学年")
    assignment_type: Optional[TeachingAssignmentTypeEnum] = Field(None, description="任务类型")
    is_active: Optional[bool] = Field(None, description="是否激活")


# ============================================================================
# 响应模型
# ============================================================================

class TeacherTeachingAssignmentResponse(TeacherTeachingAssignmentBase):
    """教师教学任务响应模型"""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    # 关联对象（可选，通过selectinload加载）
    # 注意：SchoolResponse和ClassroomResponse在api/v1/admin_organization.py中定义
    # 这里使用Any类型，实际使用时通过model_validate自动转换
    teacher: Optional[dict] = None  # UserResponse
    school: Optional[dict] = None  # SchoolResponse (定义在api/v1/admin_organization.py)
    grade: Optional[dict] = None  # GradeResponse
    classroom: Optional[dict] = None  # ClassroomResponse (定义在api/v1/admin_organization.py)
    subject: Optional[dict] = None  # SubjectResponse
    semester: Optional[dict] = None  # SemesterResponse
    
    class Config:
        from_attributes = True


# ============================================================================
# 列表响应模型
# ============================================================================

class TeacherTeachingAssignmentListResponse(BaseModel):
    """教师教学任务列表响应"""
    
    assignments: List[TeacherTeachingAssignmentResponse] = Field(default_factory=list, description="教学任务列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    
    class Config:
        from_attributes = True


# ============================================================================
# 类型前向引用（避免循环导入）
# ============================================================================

# 注意：SchoolResponse和ClassroomResponse定义在api/v1/admin_organization.py中
# 在响应模型中，我们使用dict类型，实际返回时会自动序列化


# ============================================================================
# 批量导入响应模型
# ============================================================================

class TeacherAssignmentImportError(BaseModel):
    """教师教学任务导入错误"""
    row: int = Field(..., description="行号")
    field: Optional[str] = Field(None, description="字段名")
    message: str = Field(..., description="错误信息")


class CreatedTeacherInfo(BaseModel):
    """新创建的教师信息"""
    teacher_name: str = Field(..., description="教师姓名")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., description="初始密码")
    school_name: str = Field(..., description="学校名称")
    school_code: str = Field(..., description="学校编码")
    grade_name: Optional[str] = Field(None, description="年级名称")
    classroom_code: Optional[str] = Field(None, description="班级编码")
    classroom_name: Optional[str] = Field(None, description="班级名称")
    row_number: int = Field(..., description="Excel行号")


class CreatedSemesterInfo(BaseModel):
    """新创建的学期信息"""
    semester_name: str = Field(..., description="学期名称")
    academic_year: str = Field(..., description="学年")
    semester_number: int = Field(..., description="学期编号（1或2）")
    semester_type: str = Field(..., description="学期类型（up或down）")
    start_date: Optional[str] = Field(None, description="开始日期（ISO格式）")
    end_date: Optional[str] = Field(None, description="结束日期（ISO格式）")
    row_number: int = Field(..., description="Excel行号")


class TeacherAssignmentImportResponse(BaseModel):
    """教师教学任务批量导入响应"""
    total: int = Field(..., description="总记录数")
    success: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")
    created: int = Field(0, description="创建的任务数")
    updated: int = Field(0, description="更新的任务数")
    skipped: int = Field(0, description="跳过的任务数（已存在）")
    errors: List[TeacherAssignmentImportError] = Field(default_factory=list, description="错误列表")
    created_teachers: List[CreatedTeacherInfo] = Field(default_factory=list, description="新创建的教师列表（如果启用自动创建）")
    created_semesters: List[CreatedSemesterInfo] = Field(default_factory=list, description="新创建的学期列表（如果启用自动创建）")