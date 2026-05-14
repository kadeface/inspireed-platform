"""
Form Cell（表单单元格）Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ==================== Form Option Schemas ====================


class FormOptionCreate(BaseModel):
    """创建表单选项Schema"""

    text: str = Field(..., description="选项文本")
    order: int = Field(0, description="显示顺序")
    image_url: Optional[str] = Field(None, description="图片URL")


class FormOptionResponse(BaseModel):
    """表单选项响应Schema"""

    id: Optional[str] = Field(None, description="选项ID")
    text: str
    order: int
    image_url: Optional[str] = None


# ==================== Form Cell Schemas ====================


class FormCellCreate(BaseModel):
    """创建表单单元格请求Schema"""

    cell_type: str = Field(..., description="表单类型: single_choice, multiple_choice, ranking")
    title: str = Field(..., min_length=1, max_length=200, description="表单标题")
    description: Optional[str] = Field(None, max_length=1000, description="表单描述")
    options: List[FormOptionCreate] = Field(..., min_items=2, description="选项列表")
    settings: Dict[str, Any] = Field(default_factory=dict, description="表单设置")
    time_limit: Optional[int] = Field(
        None,
        ge=10,
        le=600,
        description="时间限制（秒）"
    )


class FormCellUpdate(BaseModel):
    """更新表单单元格请求Schema"""

    cell_type: Optional[str] = Field(None, description="表单类型")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="表单标题")
    description: Optional[str] = Field(None, max_length=1000, description="表单描述")
    options: Optional[List[FormOptionCreate]] = Field(None, min_items=2, description="选项列表")
    settings: Optional[Dict[str, Any]] = Field(None, description="表单设置")
    time_limit: Optional[int] = Field(
        None,
        ge=10,
        le=600,
        description="时间限制（秒）"
    )


class FormCellResponse(BaseModel):
    """表单单元格响应Schema"""

    id: int
    lesson_id: Optional[int]
    project_cell_id: Optional[int]
    cell_type: str
    title: Optional[str]
    description: Optional[str]
    options: List[FormOptionResponse]
    settings: Dict[str, Any]
    time_limit: Optional[int]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Form Response Schemas ====================


class FormResponseCreate(BaseModel):
    """提交表单答案请求Schema"""

    answers: List[Dict[str, Any]] = Field(..., description="用户答案列表")
    session_id: Optional[int] = Field(None, description="会话ID（可选）")
    user_id: Optional[int] = Field(None, description="用户ID（可选，匿名用户可为空）")


class FormResponseResponse(BaseModel):
    """表单答案响应Schema"""

    id: int
    form_cell_id: int
    answers: List[Dict[str, Any]]
    submitted_at: datetime
    session_id: Optional[int]
    user_id: Optional[int]

    class Config:
        from_attributes = True


# ==================== Form Results Schemas ====================


class FormResults(BaseModel):
    """表单结果统计响应Schema"""

    form_cell_id: int
    total_responses: int = Field(..., ge=0, description="总回答数")
    option_stats: List[Dict[str, Any]] = Field(..., description="选项统计")
    response_rate: float = Field(..., ge=0, le=100, description="响应率（百分比）")

    class Config:
        from_attributes = True