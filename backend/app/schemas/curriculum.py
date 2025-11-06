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
