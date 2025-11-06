"""
日志模型
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ExecutionStatus(str, Enum):
    """执行状态"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ExecutionLog(Base):
    """执行日志模型"""

    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)

    # 关联的教案和Cell
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=False)

    # 执行者
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 执行状态
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)

    # 输入参数
    input_params = Column(JSON, nullable=True)

    # 输出结果
    output = Column(JSON, nullable=True)

    # 错误信息
    error_message = Column(Text, nullable=True)

    # 执行耗时（秒）
    duration = Column(Float, nullable=True)

    # 执行环境（JupyterLite / JupyterHub）
    execution_env = Column(String(50), nullable=True)

    # 时间戳
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # 关联关系
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    cell = relationship("Cell", foreign_keys=[cell_id])
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<ExecutionLog(id={self.id}, status={self.status}, user_id={self.user_id})>"


class QARecord(Base):
    """问答记录模型"""

    __tablename__ = "qa_records"

    id = Column(Integer, primary_key=True, index=True)

    # 关联的教案和Cell（可选）
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=True)

    # 提问者
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 问题
    question = Column(Text, nullable=False)

    # 回答
    answer = Column(Text, nullable=True)

    # 是否AI回答
    is_ai_answer = Column(Boolean, default=False, nullable=False)

    # 回答者（如果是教师回答）
    answerer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 标签（自动生成）
    tags = Column(JSON, nullable=True, default=list)

    # 评分（学生对回答的评分）
    rating = Column(Integer, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    answered_at = Column(DateTime, nullable=True)

    # 关联关系
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    cell = relationship("Cell", foreign_keys=[cell_id])
    user = relationship("User", foreign_keys=[user_id])
    answerer = relationship("User", foreign_keys=[answerer_id])

    def __repr__(self) -> str:
        return f"<QARecord(id={self.id}, user_id={self.user_id}, is_ai={self.is_ai_answer})>"
