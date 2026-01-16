"""课室管理 Pydantic schemas"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    """课室基础 schema"""

    name: str = Field(..., description="课室名称")
    code: Optional[str] = Field(None, description="课室编码")
    school_id: int = Field(..., description="所属学校ID")
    building: Optional[str] = Field(None, description="楼栋")
    floor: Optional[int] = Field(None, description="楼层")
    room_type: str = Field(..., description="课室类型")
    capacity: Optional[int] = Field(None, description="座位容量")
    equipment: Optional[List[str]] = Field(None, description="设备清单")
    assigned_classroom_id: Optional[int] = Field(None, description="固定分配的班级ID")
    is_active: bool = Field(True, description="是否激活")
    description: Optional[str] = Field(None, description="课室描述")


class RoomCreate(RoomBase):
    """创建课室 schema"""

    pass


class RoomUpdate(BaseModel):
    """更新课室 schema"""

    name: Optional[str] = None
    code: Optional[str] = None
    school_id: Optional[int] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    equipment: Optional[List[str]] = None
    assigned_classroom_id: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class RoomResponse(RoomBase):
    """课室响应 schema"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    """课室列表响应 schema"""

    rooms: List[RoomResponse]
    total: int
    page: int
    size: int
    total_pages: int


class RoomImportError(BaseModel):
    """课室导入错误"""

    row: int
    field: Optional[str] = None
    message: str


class RoomImportResponse(BaseModel):
    """课室导入响应"""

    total: int
    success: int
    failed: int
    created: int
    updated: int
    skipped: int
    errors: List[RoomImportError]
