"""
问答系统数据模型
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class QuestionStatus(str, enum.Enum):
    """问题状态"""

    PENDING = "pending"  # 待回答
    ANSWERED = "answered"  # 已回答
    RESOLVED = "resolved"  # 已解决（学生确认）
    CLOSED = "closed"  # 已关闭


class AskType(str, enum.Enum):
    """提问类型"""

    TEACHER = "teacher"  # 仅向教师提问
    AI = "ai"  # 仅向AI提问
    BOTH = "both"  # 同时向教师和AI提问


class AnswererType(str, enum.Enum):
    """回答者类型"""

    TEACHER = "teacher"  # 教师回答
    AI = "ai"  # AI回答


class Question(Base):
    """学生问题表"""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=True)  # 可选，针对具体单元

    # 提问者
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 问题内容
    title = Column(String(200), nullable=False)  # 问题标题
    content = Column(Text, nullable=False)  # 问题详情

    # 问题类型
    ask_type = Column(
        SQLEnum(AskType, values_callable=lambda x: [e.value for e in x]),
        default=AskType.TEACHER,
        nullable=False,
    )

    # 状态
    status = Column(
        SQLEnum(QuestionStatus, values_callable=lambda x: [e.value for e in x]),
        default=QuestionStatus.PENDING,
        nullable=False,
        index=True,
    )

    # 可见性
    is_public = Column(Boolean, default=True, nullable=False)  # 是否公开（其他学生可见）
    is_pinned = Column(Boolean, default=False, nullable=False)  # 是否置顶

    # 统计
    views = Column(Integer, default=0, nullable=False)  # 查看次数
    upvotes = Column(Integer, default=0, nullable=False)  # 点赞数

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    lesson = relationship("Lesson", back_populates="questions")
    cell = relationship("Cell", foreign_keys=[cell_id])
    student = relationship("User", foreign_keys=[student_id], back_populates="questions_asked")
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Answer.created_at",
    )
    votes = relationship("QuestionVote", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, title={self.title}, status={self.status})>"


class Answer(Base):
    """回答表（教师/AI回答）"""

    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)

    # 关联问题
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)

    # 回答者信息
    answerer_type = Column(
        SQLEnum(AnswererType, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    answerer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    # 如果是教师回答，存储教师ID；如果是AI回答，为NULL

    # 回答内容（使用Cell模块！）
    content = Column(JSON, nullable=False)
    # 格式：[{cell}, {cell}, ...]
    # 与Lesson的content字段格式完全一致

    # AI相关
    ai_model = Column(String(50), nullable=True)  # AI模型名称 (e.g., "gpt-4")
    ai_prompt_tokens = Column(Integer, nullable=True)  # 消耗的token数
    ai_completion_tokens = Column(Integer, nullable=True)

    # 质量评价
    rating = Column(Integer, nullable=True)  # 学生评分 1-5星
    is_accepted = Column(Boolean, default=False, nullable=False)  # 是否被采纳（最佳答案）

    # 统计
    upvotes = Column(Integer, default=0, nullable=False)  # 点赞数

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    question = relationship("Question", back_populates="answers")
    answerer = relationship("User", foreign_keys=[answerer_id], back_populates="answers_given")
    votes = relationship("QuestionVote", back_populates="answer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Answer(id={self.id}, question_id={self.question_id}, type={self.answerer_type})>"


class QuestionVote(Base):
    """问题/回答点赞表"""

    __tablename__ = "question_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    user = relationship("User")
    question = relationship("Question", back_populates="votes")
    answer = relationship("Answer", back_populates="votes")

    def __repr__(self) -> str:
        if self.question_id:
            return f"<QuestionVote(user={self.user_id}, question={self.question_id})>"
        else:
            return f"<QuestionVote(user={self.user_id}, answer={self.answer_id})>"
