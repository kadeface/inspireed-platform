"""
教师职务类型相关 Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# 基础模型
# ============================================================================

class TeacherPositionTypeBase(BaseModel):
    """教师职务类型基础模型"""
    
    name: str = Field(..., max_length=50, description="职务名称，如：班主任、学科教师、校长、教研室主任")
    code: Optional[str] = Field(None, max_length=50, description="职务代码，如：head_teacher、subject_teacher、principal")
    description: Optional[str] = Field(None, description="职务描述")
    category: Optional[str] = Field(None, max_length=50, description="职务分类，如：教学类、管理类、行政类")
    sort_order: int = Field(0, description="排序权重，数字越小越靠前")
    is_active: bool = Field(True, description="是否激活")


# ============================================================================
# 请求模型
# ============================================================================

class TeacherPositionTypeCreate(TeacherPositionTypeBase):
    """创建教师职务类型请求"""
    pass


class TeacherPositionTypeUpdate(BaseModel):
    """更新教师职务类型请求"""
    
    name: Optional[str] = Field(None, max_length=50, description="职务名称")
    code: Optional[str] = Field(None, max_length=50, description="职务代码")
    description: Optional[str] = Field(None, description="职务描述")
    category: Optional[str] = Field(None, max_length=50, description="职务分类")
    sort_order: Optional[int] = Field(None, description="排序权重")
    is_active: Optional[bool] = Field(None, description="是否激活")


# ============================================================================
# 响应模型
# ============================================================================

class TeacherPositionTypeResponse(TeacherPositionTypeBase):
    """教师职务类型响应模型"""
    
    id: int
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeacherPositionTypeListResponse(BaseModel):
    """教师职务类型列表响应"""
    
    position_types: List[TeacherPositionTypeResponse] = Field(default_factory=list, description="职务类型列表")
    total: int = Field(..., description="总记录数")
    
    class Config:
        from_attributes = True
