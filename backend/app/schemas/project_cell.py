"""
项目Cell Schemas
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.models.cell import CellType
from app.models.student_project import ProjectStage


class ProjectCellBase(BaseModel):
    """项目Cell基础Schema"""

    stage: ProjectStage = Field(..., description="所属5E阶段")
    cell_type: CellType = Field(..., description="Cell类型")
    title: Optional[str] = Field(None, max_length=200, description="Cell标题")
    content: Dict[str, Any] = Field(default_factory=dict, description="Cell内容")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Cell配置")
    order: int = Field(0, description="显示顺序")


class ProjectCellCreate(ProjectCellBase):
    """创建项目Cell Schema"""

    project_id: int = Field(..., description="所属项目ID")


class ProjectCellUpdate(BaseModel):
    """更新项目Cell Schema"""

    title: Optional[str] = Field(None, max_length=200, description="Cell标题")
    content: Optional[Dict[str, Any]] = Field(None, description="Cell内容")
    config: Optional[Dict[str, Any]] = Field(None, description="Cell配置")
    order: Optional[int] = Field(None, description="显示顺序")


class ProjectCellResponse(ProjectCellBase):
    """项目Cell响应Schema"""

    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectCellListResponse(BaseModel):
    """项目Cell列表响应Schema"""

    items: List[ProjectCellResponse]
    total: int

