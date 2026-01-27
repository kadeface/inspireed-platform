"""
学科教研组相关的Pydantic模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.subject_group import GroupScope, MemberRole


# ==================== 教研组相关 ====================


class SubjectGroupBase(BaseModel):
    """教研组基础信息"""

    name: str = Field(..., description="教研组名称")
    description: Optional[str] = Field(None, description="教研组描述")
    subject_id: int = Field(..., description="学科ID")
    grade_id: Optional[int] = Field(None, description="年级ID（可选）")
    scope: GroupScope = Field(..., description="教研组范围")
    school_id: Optional[int] = Field(None, description="学校ID（校级）")
    region_id: Optional[int] = Field(None, description="区域ID（区域级）")
    is_public: bool = Field(False, description="是否公开")
    cover_image_url: Optional[str] = Field(None, description="封面图URL")


class SubjectGroupCreate(SubjectGroupBase):
    """创建教研组请求"""

    pass


class SubjectGroupUpdate(BaseModel):
    """更新教研组请求"""

    name: Optional[str] = None
    description: Optional[str] = None
    grade_id: Optional[int] = None
    is_public: Optional[bool] = None
    cover_image_url: Optional[str] = None


class SubjectGroupInDB(SubjectGroupBase):
    """数据库中的教研组"""

    id: int
    creator_id: int
    is_active: bool
    member_count: int
    lesson_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubjectGroupResponse(SubjectGroupInDB):
    """教研组响应"""

    # 可以包含额外的关联信息
    subject_name: Optional[str] = None
    grade_name: Optional[str] = None
    school_name: Optional[str] = None
    region_name: Optional[str] = None
    creator_name: Optional[str] = None
    user_role: Optional[MemberRole] = None  # 当前用户在该组的角色


# ==================== 成员关系相关 ====================


class GroupMembershipBase(BaseModel):
    """成员关系基础信息"""

    group_id: int = Field(..., description="教研组ID")
    user_id: int = Field(..., description="用户ID")
    role: MemberRole = Field(MemberRole.MEMBER, description="成员角色")


class GroupMembershipCreate(BaseModel):
    """添加成员请求"""

    user_id: int = Field(..., description="用户ID")
    role: MemberRole = Field(MemberRole.MEMBER, description="成员角色")


class GroupMembershipUpdate(BaseModel):
    """更新成员请求"""

    role: Optional[MemberRole] = None
    is_active: Optional[bool] = None


class GroupMembershipInDB(GroupMembershipBase):
    """数据库中的成员关系"""

    id: int
    is_active: bool
    joined_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GroupMembershipResponse(GroupMembershipInDB):
    """成员关系响应"""

    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_avatar_url: Optional[str] = None


# ==================== 共享教学设计相关 ====================


class SharedLessonBase(BaseModel):
    """共享教学设计基础信息"""

    group_id: int = Field(..., description="教研组ID")
    lesson_id: int = Field(..., description="教案ID")
    share_note: Optional[str] = Field(None, description="分享说明")


class SharedLessonCreate(BaseModel):
    """创建共享教学设计请求"""

    lesson_id: int = Field(..., description="教案ID")
    share_note: Optional[str] = Field(None, description="分享说明")


class SharedLessonUpdate(BaseModel):
    """更新共享教学设计请求"""

    share_note: Optional[str] = None
    is_active: Optional[bool] = None


class SharedLessonInDB(SharedLessonBase):
    """数据库中的共享教学设计"""

    id: int
    sharer_id: int
    is_active: bool
    view_count: int
    download_count: int
    like_count: int
    shared_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SharedLessonResponse(SharedLessonInDB):
    """共享教学设计响应"""

    lesson_title: Optional[str] = None
    lesson_description: Optional[str] = None
    lesson_cover_image_url: Optional[str] = None
    lesson_cell_count: Optional[int] = None
    lesson_estimated_duration: Optional[int] = None
    sharer_name: Optional[str] = None
    sharer_avatar_url: Optional[str] = None
    group_name: Optional[str] = None


# ==================== 列表响应 ====================


class SubjectGroupListResponse(BaseModel):
    """教研组列表响应"""

    items: List[SubjectGroupResponse]
    total: int
    page: int
    page_size: int


class GroupMembershipListResponse(BaseModel):
    """成员列表响应"""

    items: List[GroupMembershipResponse]
    total: int
    page: int
    page_size: int


class SharedLessonListResponse(BaseModel):
    """共享教学设计列表响应"""

    items: List[SharedLessonResponse]
    total: int
    page: int
    page_size: int


# ==================== 统计信息 ====================


class SubjectGroupStatistics(BaseModel):
    """教研组统计信息"""

    total_groups: int = Field(..., description="总教研组数")
    total_members: int = Field(..., description="总成员数")
    total_shared_lessons: int = Field(..., description="总共享教案数")
    my_groups: int = Field(..., description="我的教研组数")
    my_shared_lessons: int = Field(..., description="我的共享教案数")
