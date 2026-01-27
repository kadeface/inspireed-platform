"""
学生项目模型
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProjectStatus(str, Enum):
    """项目状态枚举"""

    DRAFT = "draft"  # 草稿
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    SUBMITTED = "submitted"  # 已提交


class ProjectStage(str, Enum):
    """5E阶段枚举"""

    ENGAGE = "engage"  # 参与投入
    EXPLORE = "explore"  # 探索发现
    EXPLAIN = "explain"  # 解释建构
    ELABORATE = "elaborate"  # 深化拓展
    EVALUATE = "evaluate"  # 评价反思


class StudentProject(Base):
    """学生项目模型"""

    __tablename__ = "student_projects"

    id = Column(Integer, primary_key=True, index=True)

    # 基本信息
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # 项目创建者（学生）
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 项目类型
    project_type = Column(
        String(50), nullable=True, comment="项目类型：scientific_inquiry, engineering_design, data_analysis等"
    )

    # 项目状态
    status = Column(
        SQLEnum(
            ProjectStatus,
            name="projectstatus",
            native_enum=True,
            create_constraint=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=ProjectStatus.DRAFT,
        nullable=False,
        index=True,
    )

    # 5E阶段内容（JSON格式，存储每个阶段的Cell配置）
    engage_content = Column(JSON, nullable=False, default=list, comment="Engage阶段内容")
    explore_content = Column(JSON, nullable=False, default=list, comment="Explore阶段内容")
    explain_content = Column(JSON, nullable=False, default=list, comment="Explain阶段内容")
    elaborate_content = Column(JSON, nullable=False, default=list, comment="Elaborate阶段内容")
    evaluate_content = Column(JSON, nullable=False, default=list, comment="Evaluate阶段内容")

    # 完成度（每个阶段的完成百分比）
    completion = Column(
        JSON,
        nullable=False,
        default=dict,
        comment='完成度，格式: {"engage": 0, "explore": 0, "explain": 0, "elaborate": 0, "evaluate": 0}',
    )

    # 协作信息（为未来功能预留）
    is_team_project = Column(Boolean, default=False, nullable=False, comment="是否为团队项目")
    team_members = Column(JSON, nullable=False, default=list, comment="团队成员ID列表")

    # 封面图
    cover_image_url = Column(String(500), nullable=True, comment="封面图片URL")

    # 标签
    tags = Column(JSON, nullable=False, default=list, comment="项目标签列表")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    submitted_at = Column(DateTime, nullable=True, comment="提交时间")

    # 关联关系
    creator = relationship("User", foreign_keys=[creator_id])

    def __repr__(self) -> str:
        return f"<StudentProject(id={self.id}, title={self.title}, status={self.status})>"

