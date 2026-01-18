"""
年级考试科目配置相关的 Pydantic Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GradeSubjectConfigBase(BaseModel):
    """年级考试科目配置基础模型"""

    grade_id: int = Field(..., description="年级ID")
    subject_id: int = Field(..., description="学科ID")
    full_score: int = Field(100, ge=1, le=1000, description="满分")
    pass_line: int = Field(60, ge=0, le=1000, description="及格线")
    excellent_line: int = Field(85, ge=0, le=1000, description="优秀线")
    good_line: int = Field(75, ge=0, le=1000, description="良好线")
    display_order: int = Field(0, ge=0, description="显示顺序")
    description: Optional[str] = Field(None, max_length=200, description="备注说明")


class GradeSubjectConfigCreate(GradeSubjectConfigBase):
    """创建年级考试科目配置"""

    pass


class GradeSubjectConfigUpdate(BaseModel):
    """更新年级考试科目配置"""

    full_score: Optional[int] = Field(None, ge=1, le=1000, description="满分")
    pass_line: Optional[int] = Field(None, ge=0, le=1000, description="及格线")
    excellent_line: Optional[int] = Field(None, ge=0, le=1000, description="优秀线")
    good_line: Optional[int] = Field(None, ge=0, le=1000, description="良好线")
    display_order: Optional[int] = Field(None, ge=0, description="显示顺序")
    description: Optional[str] = Field(None, max_length=200, description="备注说明")
    is_active: Optional[bool] = Field(None, description="是否启用")


class GradeSubjectConfigResponse(GradeSubjectConfigBase):
    """年级考试科目配置响应模型"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]

    # 嵌套关联信息
    grade_name: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None

    class Config:
        from_attributes = True


class GradeSubjectsWithScores(BaseModel):
    """年级及其所有考试科目配置（用于前端展示）"""

    grade_id: int
    grade_name: str
    grade_level: int
    subjects: list[GradeSubjectConfigResponse]


class BulkCreateGradeSubjectConfig(BaseModel):
    """批量创建年级考试科目配置"""

    configs: list[GradeSubjectConfigCreate] = Field(
        ...,
        min_items=1,
        description="要创建的配置列表"
    )
