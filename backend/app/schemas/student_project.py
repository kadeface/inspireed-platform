"""
学生项目Schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

from app.models.student_project import ProjectStatus


class StudentProjectBase(BaseModel):
    """项目基础Schema"""

    title: str = Field(..., min_length=1, max_length=200, description="项目标题")
    description: Optional[str] = Field(None, description="项目描述")
    project_type: Optional[str] = Field(None, description="项目类型")


class StudentProjectCreate(StudentProjectBase):
    """项目创建Schema"""

    pass


class StudentProjectUpdate(BaseModel):
    """项目更新Schema"""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="项目标题")
    description: Optional[str] = Field(None, description="项目描述")
    status: Optional[ProjectStatus] = Field(None, description="项目状态")
    cover_image_url: Optional[str] = Field(None, max_length=500, description="封面图片URL")
    tags: Optional[List[str]] = Field(None, description="项目标签列表")
    # 5E阶段内容更新
    engage_content: Optional[List[Dict[str, Any]]] = Field(None, description="Engage阶段内容")
    explore_content: Optional[List[Dict[str, Any]]] = Field(None, description="Explore阶段内容")
    explain_content: Optional[List[Dict[str, Any]]] = Field(None, description="Explain阶段内容")
    elaborate_content: Optional[List[Dict[str, Any]]] = Field(None, description="Elaborate阶段内容")
    evaluate_content: Optional[List[Dict[str, Any]]] = Field(None, description="Evaluate阶段内容")

    @field_validator("engage_content", "explore_content", "explain_content", "elaborate_content", "evaluate_content", mode="before")
    @classmethod
    def validate_content(cls, v):
        """验证阶段内容字段"""
        if v is None:
            return None
        if not isinstance(v, list):
            return []
        return v


class StudentProjectResponse(StudentProjectBase):
    """项目响应Schema"""

    id: int
    creator_id: int
    creator_name: Optional[str] = None
    project_type: Optional[str] = None
    status: ProjectStatus
    completion: Dict[str, int] = Field(default_factory=dict, description="各阶段完成度")
    engage_content: List[Dict[str, Any]] = Field(default_factory=list, description="Engage阶段内容")
    explore_content: List[Dict[str, Any]] = Field(default_factory=list, description="Explore阶段内容")
    explain_content: List[Dict[str, Any]] = Field(default_factory=list, description="Explain阶段内容")
    elaborate_content: List[Dict[str, Any]] = Field(default_factory=list, description="Elaborate阶段内容")
    evaluate_content: List[Dict[str, Any]] = Field(default_factory=list, description="Evaluate阶段内容")
    cover_image_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_team_project: bool = False
    team_members: List[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentProjectListResponse(BaseModel):
    """项目列表响应Schema"""

    items: List[StudentProjectResponse]
    total: int
    page: int
    page_size: int


class StageContentUpdate(BaseModel):
    """阶段内容更新Schema"""

    content: List[Dict[str, Any]] = Field(..., description="阶段内容列表")

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v):
        """验证内容字段"""
        if v is None:
            return []
        if not isinstance(v, list):
            return []
        return v

