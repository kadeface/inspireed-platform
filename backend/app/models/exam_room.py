"""考试考场安排模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Index as SQLIndex, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ExamRoom(Base):
    """考场模型"""
    __tablename__ = "exam_rooms"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True, comment="考试ID")
    name = Column(String(100), nullable=False, comment="考场名称：第1考场")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, comment="学校ID")
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True, comment="使用的教室ID")
    capacity = Column(Integer, nullable=False, default=30, comment="考场容量")
    seat_count = Column(Integer, nullable=False, default=0, comment="实际座位数")

    # 考号范围
    exam_number_start = Column(String(20), nullable=True, comment="起始考号")
    exam_number_end = Column(String(20), nullable=True, comment="结束考号")

    # 考场配置
    arrangement_type = Column(String(20), nullable=False, default="by_class", comment="编排类型：by_class/mixed")
    seat_pattern = Column(String(20), nullable=False, default="s_shape", comment="座位排列：sequential/s_shape")

    # 标准字段
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    exam = relationship("Exam", back_populates="exam_rooms")
    school = relationship("School")
    room = relationship("Room")
    students = relationship("ExamRoomStudent", back_populates="exam_room", cascade="all, delete-orphan")
    proctors = relationship("ExamProctor", back_populates="exam_room", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ExamRoom(id={self.id}, name={self.name}, exam_id={self.exam_id})>"


class ExamRoomStudent(Base):
    """考场学生关联模型"""
    __tablename__ = "exam_room_students"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("exam_rooms.id", ondelete="CASCADE"), nullable=False, index=True, comment="考场ID")
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="学生ID")
    exam_number = Column(String(20), nullable=False, comment="考号")
    seat_number = Column(Integer, nullable=False, comment="座位号 1-30")
    table_number = Column(Integer, nullable=True, comment="桌子号（可选）")

    # 冗余字段（加速查询）
    student_id_number = Column(String(50), nullable=True, comment="学籍号")
    student_name = Column(String(100), nullable=True, comment="学生姓名（快照）")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True, comment="学校ID")
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True, comment="班级ID")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    exam_room = relationship("ExamRoom", back_populates="students")
    student = relationship("User")
    school = relationship("School")
    classroom = relationship("Classroom")

    # 约束
    __table_args__ = (
        UniqueConstraint('room_id', 'exam_number', name='uq_room_exam_number'),
        UniqueConstraint('room_id', 'seat_number', name='uq_room_seat_number'),
    )

    def __repr__(self) -> str:
        return f"<ExamRoomStudent(id={self.id}, room_id={self.room_id}, exam_number={self.exam_number})>"


class ExamProctor(Base):
    """监考教师模型"""
    __tablename__ = "exam_proctors"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("exam_rooms.id", ondelete="CASCADE"), nullable=False, index=True, comment="考场ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="教师用户ID")
    proctor_type = Column(String(20), nullable=False, comment="监考类型：primary/assistant")
    responsibilities = Column(JSON, nullable=True, comment="职责列表")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    exam_room = relationship("ExamRoom", back_populates="proctors")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<ExamProctor(id={self.id}, room_id={self.room_id}, user_id={self.user_id}, type={self.proctor_type})>"
