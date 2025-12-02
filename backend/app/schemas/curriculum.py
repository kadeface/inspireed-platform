"""
课程体系相关的 Pydantic Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# Subject Schemas
class SubjectBase(BaseModel):
    """学科基础模型"""

    name: str = Field(..., max_length=100, description="学科名称")
    code: str = Field(..., max_length=50, description="学科代码")
    description: Optional[str] = Field(None, description="学科描述")
    display_order: int = Field(0, description="显示顺序")


class SubjectResponse(SubjectBase):
    """学科响应模型"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubjectToggle(BaseModel):
    """学科启用/禁用模型"""

    is_active: bool


# Grade Schemas
class GradeBase(BaseModel):
    """年级基础模型"""

    name: str = Field(..., max_length=50, description="年级名称")
    level: int = Field(..., ge=1, le=12, description="年级级别 (1-12)")


class GradeResponse(GradeBase):
    """年级响应模型"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GradeToggle(BaseModel):
    """年级启用/禁用模型"""

    is_active: bool


# Course Schemas
class CourseBase(BaseModel):
    """课程基础模型"""

    subject_id: int = Field(..., description="学科ID")
    grade_id: int = Field(..., description="年级ID")
    name: str = Field(..., max_length=200, description="课程名称")
    code: Optional[str] = Field(None, max_length=100, description="课程代码")
    description: Optional[str] = Field(None, description="课程描述")
    display_order: int = Field(0, description="显示顺序")


class CourseCreate(CourseBase):
    """创建课程模型"""

    pass


class CourseUpdate(BaseModel):
    """更新课程模型"""

    name: Optional[str] = Field(None, max_length=200, description="课程名称")
    code: Optional[str] = Field(None, max_length=100, description="课程代码")
    description: Optional[str] = Field(None, description="课程描述")
    display_order: Optional[int] = Field(None, description="显示顺序")
    is_active: Optional[bool] = Field(None, description="是否启用")
    grade_id: Optional[int] = Field(None, description="年级ID（调整课程年级）")


class CourseResponse(CourseBase):
    """课程响应模型"""

    id: int
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    # 嵌套关联信息
    subject: Optional[SubjectResponse] = None
    grade: Optional[GradeResponse] = None

    class Config:
        from_attributes = True


class CourseMergeRequest(BaseModel):
    """课程合并请求模型"""
    
    source_course_id: int = Field(..., description="源课程ID（将被合并的课程）")
    target_course_id: int = Field(..., description="目标课程ID（保留的课程）")
    merge_lessons: bool = Field(True, description="是否合并教案")
    merge_chapters: bool = Field(True, description="是否合并章节")
    handle_conflicts: str = Field("rename", description="冲突处理方式: rename(重命名), skip(跳过), overwrite(覆盖)")


class CourseMergeResponse(BaseModel):
    """课程合并响应模型"""
    
    success: bool
    target_course: CourseResponse
    merged_lessons_count: int = 0
    merged_chapters_count: int = 0
    skipped_lessons_count: int = 0
    skipped_chapters_count: int = 0
    errors: List[str] = []


# Curriculum Tree Schemas
class CourseTreeNode(BaseModel):
    """课程树节点"""

    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    is_active: bool
    lesson_count: int = 0


class GradeTreeNode(BaseModel):
    """年级树节点"""

    id: int
    name: str
    level: int
    is_active: bool
    courses: List[CourseTreeNode] = []
    lesson_count: int = 0


class SubjectTreeNode(BaseModel):
    """学科树节点"""

    id: int
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    grades: List[GradeTreeNode] = []
    lesson_count: int = 0


class CurriculumTreeResponse(BaseModel):
    """课程体系树形响应"""

    subjects: List[SubjectTreeNode]
    total_subjects: int
    total_grades: int
    total_courses: int
    total_lessons: int


# Chapter Tree Schemas
class ChapterTreeNode(BaseModel):
    """章节树节点"""

    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    display_order: int
    parent_id: Optional[int]
    lesson_count: int = 0
    children: List["ChapterTreeNode"] = []


class CourseWithChaptersResponse(BaseModel):
    """课程及其章节树形响应"""

    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    subject: Optional[SubjectResponse]
    grade: Optional[GradeResponse]
    chapters: List[ChapterTreeNode]
    total_chapters: int
    total_lessons: int


# 支持递归引用
ChapterTreeNode.model_rebuild()
