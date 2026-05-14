"""
Form Cell（表单单元格）模型
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    JSON,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class FormCell(Base):
    """FormCell表单单元格模型"""

    __tablename__ = "form_cells"
    __table_args__ = (
        Index("ix_form_cells_lesson_id", "lesson_id"),
        Index("ix_form_cells_project_cell_id", "project_cell_id"),
    )

    id = Column(Integer, primary_key=True, index=True)

    # 所属课程（可选）
    lesson_id = Column(
        Integer, ForeignKey("lessons.id"), nullable=True, index=True
    )

    # 所属项目单元格（可选）
    project_cell_id = Column(
        Integer, ForeignKey("project_cells.id"), nullable=True, index=True
    )

    # 表单单元格类型
    cell_type = Column(String, nullable=True, comment="表单单元格类型")

    # 标题
    title = Column(String(200), nullable=True, comment="表单标题")

    # 描述
    description = Column(Text, nullable=True, comment="表单描述")

    # 选项配置（JSON格式）
    options = Column(
        JSON, nullable=False, default=dict, comment="表单选项配置"
    )

    # 设置配置（JSON格式）
    settings = Column(
        JSON, nullable=False, default=dict, comment="表单设置配置"
    )

    # 时间限制（秒）
    time_limit = Column(Integer, nullable=True, comment="时间限制（秒）")

    # 创建者
    created_by = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 关联关系
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    project_cell = relationship("ProjectCell", foreign_keys=[project_cell_id])
    responses = relationship(
        "FormResponse",
        back_populates="form_cell",
        cascade="all, delete-orphan",
    )
    created_by_user = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return (
            f"<FormCell(id={self.id}, title={self.title}, "
            f"cell_type={self.cell_type}, lesson_id={self.lesson_id})>"
        )


class FormResponse(Base):
    """FormResponse表单响应模型"""

    __tablename__ = "form_responses"
    __table_args__ = (
        Index("ix_form_responses_form_cell_id", "form_cell_id"),
        Index("ix_form_responses_user_id", "user_id"),
        Index("ix_form_responses_session_id", "session_id"),
    )

    id = Column(Integer, primary_key=True, index=True)

    # 所属表单单元格
    form_cell_id = Column(
        Integer, ForeignKey("form_cells.id"), nullable=False, index=True
    )

    # 用户ID（可选，匿名用户可为空）
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # 答案列表（JSON格式）
    answers = Column(
        JSON, nullable=False, default=list, comment="用户答案列表"
    )

    # 提交时间
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 所属会话（可选）
    session_id = Column(
        Integer, ForeignKey("class_sessions.id"), nullable=True, index=True
    )

    # 关联关系
    form_cell = relationship("FormCell", back_populates="responses")
    user = relationship("User", foreign_keys=[user_id])
    session = relationship("ClassSession", foreign_keys=[session_id])

    def __repr__(self) -> str:
        return (
            f"<FormResponse(id={self.id}, form_cell_id={self.form_cell_id}, "
            f"user_id={self.user_id}, submitted_at={self.submitted_at})>"
        )