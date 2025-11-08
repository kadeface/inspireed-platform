"""
用户Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.validators import normalize_user_role
from app.models.user import UserRole


class UserBase(BaseModel):
    """用户基础Schema"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: object) -> UserRole:
        normalized = normalize_user_role(value)
        if normalized is None:
            raise ValueError("用户角色不能为空")
        return normalized


class UserCreate(UserBase):
    """用户创建Schema"""

    password: str = Field(..., min_length=6, max_length=50)
    region_id: Optional[int] = Field(None, description="所属区域ID")
    school_id: Optional[int] = Field(None, description="所属学校ID")
    grade_id: Optional[int] = Field(None, description="所属年级ID")
    classroom_id: Optional[int] = Field(None, description="所属班级ID")


class UserUpdate(BaseModel):
    """用户更新Schema"""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)
    avatar_url: Optional[str] = None
    region_id: Optional[int] = Field(None, description="所属区域ID")
    school_id: Optional[int] = Field(None, description="所属学校ID")
    grade_id: Optional[int] = Field(None, description="所属年级ID")
    classroom_id: Optional[int] = Field(None, description="所属班级ID")


class UserResponse(UserBase):
    """用户响应Schema"""

    id: int
    is_active: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    region_id: Optional[int] = None
    school_id: Optional[int] = None
    grade_id: Optional[int] = None
    classroom_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
