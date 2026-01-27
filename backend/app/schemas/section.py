"""
Section（大环节）Schema
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SectionBase(BaseModel):
    """Section 基础 Schema"""

    name: str = Field(..., description="大环节名称", max_length=200)
    type: str = Field(default="custom", description="大环节类型：default 或 custom")
    order: int = Field(default=0, description="排序顺序")
    is_collapsed: bool = Field(default=False, description="是否折叠")


class SectionCreate(SectionBase):
    """创建 Section Schema"""

    lesson_id: int = Field(..., description="所属教案ID")


class SectionUpdate(BaseModel):
    """更新 Section Schema"""

    name: Optional[str] = Field(None, description="大环节名称", max_length=200)
    order: Optional[int] = Field(None, description="排序顺序")
    is_collapsed: Optional[bool] = Field(None, description="是否折叠")


class SectionMove(BaseModel):
    """移动 Section Schema（调整顺序）"""

    new_order: int = Field(..., description="新的排序顺序")


class SectionResponse(SectionBase):
    """Section 响应 Schema"""

    id: int
    lesson_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SectionWithCells(SectionResponse):
    """包含 Cells 的 Section Schema"""

    cells: List[dict] = Field(default_factory=list, description="该大环节下的 Cell 列表")


class CellMoveRequest(BaseModel):
    """移动 Cell 到指定大环节 Schema"""

    section_id: int = Field(..., description="目标大环节ID")
    new_order: Optional[int] = Field(None, description="新的排序顺序（可选，默认插入到末尾）")
