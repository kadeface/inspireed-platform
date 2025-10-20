"""
课程体系模型
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Subject(Base):
    """学科模型"""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # 数学
    code = Column(String(50), nullable=False, unique=True)  # math
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    courses = relationship("Course", back_populates="subject", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name={self.name}, code={self.code})>"


class Grade(Base):
    """年级模型"""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)  # 一年级
    level = Column(Integer, nullable=False, unique=True)  # 1-12
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    courses = relationship("Course", back_populates="grade", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Grade(id={self.id}, name={self.name}, level={self.level})>"


class Course(Base):
    """课程模型 (学科 + 年级的组合)"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
    
    name = Column(String(200), nullable=False)  # 一年级数学
    code = Column(String(100), nullable=True)  # grade1-math
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    subject = relationship("Subject", back_populates="courses")
    grade = relationship("Grade", back_populates="courses")
    creator = relationship("User", foreign_keys=[created_by])
    lessons = relationship("Lesson", back_populates="course")
    chapters = relationship("Chapter", back_populates="course", cascade="all, delete-orphan")
    
    # 唯一约束：同一学科和年级只能有一个课程组合
    __table_args__ = (
        UniqueConstraint('subject_id', 'grade_id', name='uix_subject_grade'),
    )
    
    def __repr__(self) -> str:
        return f"<Course(id={self.id}, name={self.name})>"


class Chapter(Base):
    """章节模型"""
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)  # 支持多级章节
    
    name = Column(String(200), nullable=False)  # 第一章：集合与函数
    code = Column(String(50), nullable=True)  # chapter-1
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    course = relationship("Course", back_populates="chapters")
    parent = relationship("Chapter", remote_side=[id], backref="children")
    resources = relationship("Resource", back_populates="chapter", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Chapter(id={self.id}, name={self.name})>"


class Resource(Base):
    """课程资源模型（包括 PDF、视频等）"""
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    
    # 基本信息
    title = Column(String(200), nullable=False)  # 集合的概念 - 教学设计
    description = Column(Text, nullable=True)
    resource_type = Column(String(20), nullable=False)  # pdf, video, document, link
    
    # 文件相关（主要用于PDF）
    file_url = Column(String(500), nullable=True)  # 文件URL
    file_size = Column(Integer, nullable=True)  # 文件大小（字节）
    page_count = Column(Integer, nullable=True)  # PDF页数
    thumbnail_url = Column(String(500), nullable=True)  # 缩略图URL
    
    # 权限和状态
    is_official = Column(Boolean, default=False, nullable=False)  # 是否官方资源
    is_downloadable = Column(Boolean, default=True, nullable=False)  # 是否允许下载
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    
    # 统计
    view_count = Column(Integer, default=0, nullable=False)  # 查看次数
    download_count = Column(Integer, default=0, nullable=False)  # 下载次数
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    chapter = relationship("Chapter", back_populates="resources")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self) -> str:
        return f"<Resource(id={self.id}, title={self.title}, type={self.resource_type})>"

