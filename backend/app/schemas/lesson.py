"""
教案Schemas
"""

from datetime import datetime
from typing import Any, List, Optional, Union
from pydantic import BaseModel, Field, field_serializer, field_validator
import logging

from app.models.lesson import LessonStatus
from app.schemas.curriculum import CourseResponse

logger = logging.getLogger(__name__)


class LessonClassroomInfo(BaseModel):
    """教案关联班级信息"""

    id: int
    name: str
    school_id: int
    grade_id: int
    code: Optional[str] = None
    enrollment_year: Optional[int] = None

    class Config:
        from_attributes = True


class LessonBase(BaseModel):
    """教案基础Schema"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    tags: Optional[List[str]] = None


def _validate_content_cells(v: Any) -> Any:
    """验证 content：支持 List[dict]（旧格式）或 dict 含 sections（新格式）"""
    import logging
    logger = logging.getLogger(__name__)
    if v is None:
        return []
    # 新格式：{ "sections": [ { id, name, type, order, cells: [...] } ] }
    if isinstance(v, dict) and "sections" in v:
        return v
    if not isinstance(v, list):
        logger.warning(f"Content 既不是列表也不是 sections 对象: {type(v)}")
        return []
    original_length = len(v)
    valid_cells = []
    for idx, cell in enumerate(v):
        if cell is None or not isinstance(cell, dict):
            if cell is not None:
                logger.warning(f"Cell[{idx}] 类型无效: {type(cell)}")
            continue
        valid_cells.append(cell)
    if len(valid_cells) != original_length:
        logger.warning(f"⚠️ Content 过滤了 {original_length - len(valid_cells)} 个无效 cell")
    return valid_cells


class LessonCreate(LessonBase):
    """教案创建Schema"""

    course_id: int = Field(..., description="所属课程ID")
    chapter_id: Optional[int] = Field(None, description="所属章节ID")
    content: Union[List[dict], dict] = Field(default_factory=list)
    national_resource_id: Optional[str] = None

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v: Any) -> Any:
        return _validate_content_cells(v)


class LessonUpdate(BaseModel):
    """教案更新Schema"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    course_id: Optional[int] = Field(None, description="所属课程ID")
    chapter_id: Optional[int] = Field(None, description="所属章节ID")
    content: Optional[Union[List[dict], dict]] = None
    tags: Optional[List[str]] = None
    status: Optional[LessonStatus] = None
    cover_image_url: Optional[str] = Field(None, description="封面图片URL")

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v: Any) -> Any:
        if v is None:
            return None
        return _validate_content_cells(v)


class LessonResponse(LessonBase):
    """教案响应Schema"""

    id: int
    creator_id: int
    course_id: int
    chapter_id: Optional[int] = None
    status: LessonStatus
    content: Union[List[dict], dict]  # 旧: List[dict]，新: { "sections": [...] }
    version: int
    parent_id: Optional[int] = None
    national_resource_id: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    classroom_ids: List[int] = Field(default_factory=list)
    classrooms: List[LessonClassroomInfo] = Field(default_factory=list)

    # 教案统计（列表与详情均返回，供卡片显示单元数等）
    cell_count: int = Field(0, description="单元/cell 数量")
    estimated_duration: Optional[int] = Field(None, description="预计时长（分钟）")
    view_count: int = Field(0, description="查看次数")

    # 教师信息
    creator_name: Optional[str] = None
    creator_avatar: Optional[str] = None

    # 嵌套课程信息
    course: Optional[CourseResponse] = None

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v: Any) -> Any:
        return _validate_content_cells(v)

    @field_validator("status", mode="before")
    @classmethod
    def convert_status(cls, v):
        """Convert uppercase status values to lowercase"""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_serializer("content")
    def serialize_content(self, content: Union[List[dict], dict]) -> Union[List[dict], dict]:
        """序列化content时，将cell_type转换为type（前端兼容性）"""
        def convert_cell(cell: dict) -> dict:
            if not isinstance(cell, dict):
                return cell
            # 创建新的cell字典
            converted = {**cell}
            if "cell_type" in converted:
                # 将cell_type转换为大写并重命名为type
                cell_type_value = converted.pop("cell_type")
                if isinstance(cell_type_value, str):
                    # 确保是大写（兼容旧数据的小写值）
                    converted["type"] = cell_type_value.upper()
                else:
                    # 如果是枚举或其他类型，转换为字符串
                    converted["type"] = str(cell_type_value).upper()
            # 如果已经有type字段，确保是大写
            elif "type" in converted and isinstance(converted["type"], str):
                converted["type"] = converted["type"].upper()
            return converted

        if isinstance(content, list):
            return [convert_cell(cell) for cell in content]
        elif isinstance(content, dict) and "sections" in content:
            # 新格式：{sections: [{cells: [...]}]}
            sections = content.get("sections", [])
            converted_sections = []
            for section in sections:
                if not isinstance(section, dict):
                    converted_sections.append(section)
                    continue
                converted_section = {**section}
                if "cells" in section and isinstance(section["cells"], list):
                    converted_section["cells"] = [convert_cell(cell) for cell in section["cells"]]
                converted_sections.append(converted_section)
            return {"sections": converted_sections}
        else:
            return content

    class Config:
        from_attributes = True


class LessonListResponse(BaseModel):
    """教案列表响应"""

    items: List[LessonResponse]
    total: int
    page: int
    page_size: int


class LessonCreatorStatusCounts(BaseModel):
    """当前用户创建的教案按状态计数（工作台首屏专用，避免多次列表请求）"""

    draft: int = Field(0, description="草稿数量")
    published: int = Field(0, description="已发布数量")
    archived: int = Field(0, description="已归档数量")


class LessonPublishRequest(BaseModel):
    """教案发布请求。班级在上课时选择，发布时可不传班级。"""

    classroom_ids: List[int] = Field(
        default_factory=list,
        description="教案发布时可选的目标班级ID列表，为空表示仅发布不关联班级",
    )


class LessonRelatedMaterial(BaseModel):
    """课程关联素材信息"""

    id: int
    title: str
    summary: Optional[str] = None
    resource_type: str
    source_lesson_id: Optional[int] = None
    source_lesson_title: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    is_accessible: bool = True
    tags: List[str] = Field(default_factory=list)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LessonRelatedMaterialListResponse(BaseModel):
    """课程关联素材列表响应"""

    items: List[LessonRelatedMaterial]
    total: int
    page: int
    page_size: int
