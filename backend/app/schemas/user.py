"""
用户Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

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


class TeacherRegisterRequest(BaseModel):
    """教师公开注册 Schema"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)
    full_name: Optional[str] = None
    school_id: Optional[int] = None
    school_name: Optional[str] = Field(None, max_length=200)
    region_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_school_fields(self) -> "TeacherRegisterRequest":
        has_id = self.school_id is not None
        has_name = bool(self.school_name and self.school_name.strip())
        if has_id and has_name:
            raise ValueError("请选择已有学校或填写新学校名称，不能同时填写")
        if not has_id and not has_name:
            raise ValueError("请选择学校或填写学校名称")
        if has_name and self.school_name:
            self.school_name = self.school_name.strip()
        return self


class RegisterSchoolOption(BaseModel):
    """注册页学校选项"""

    id: int
    name: str
    region_name: Optional[str] = None


class RegisterRegionOption(BaseModel):
    """注册页区域选项"""

    id: int
    name: str
    level: int


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
    region_name: Optional[str] = None
    school_name: Optional[str] = None
    grade_name: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
