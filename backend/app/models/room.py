"""课室/物理教室模型"""

from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Room(Base):
    """课室/物理教室模型"""

    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="课室名称")
    code = Column(String(50), nullable=True, comment="课室编码")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, comment="所属学校ID")
    building = Column(String(50), nullable=True, comment="楼栋")
    floor = Column(Integer, nullable=True, comment="楼层")
    room_type = Column(String(50), nullable=False, comment="课室类型")
    capacity = Column(Integer, nullable=True, comment="座位容量")
    equipment = Column(JSON, nullable=True, comment="设备清单")
    assigned_classroom_id = Column(
        Integer,
        ForeignKey("classrooms.id"),
        nullable=True,
        comment="固定分配的班级ID",
    )
    is_active = Column(Boolean, default=True, comment="是否激活")
    description = Column(Text, nullable=True, comment="课室描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # Relationships
    school = relationship("School", back_populates="rooms")
    assigned_classroom = relationship("Classroom", foreign_keys=[assigned_classroom_id])

    def __repr__(self) -> str:
        return f"<Room(id={self.id}, name={self.name}, school_id={self.school_id})>"
