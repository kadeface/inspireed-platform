"""
组织架构相关模型
包括区域、学校等组织单位
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Region(Base):
    """区域模型（省/市/区）"""
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="区域名称")
    code = Column(String(20), unique=True, nullable=False, comment="区域编码")
    level = Column(Integer, nullable=False, comment="区域级别：1-省，2-市，3-区")
    parent_id = Column(Integer, ForeignKey("regions.id"), nullable=True, comment="父级区域ID")
    is_active = Column(Boolean, default=True, comment="是否激活")
    description = Column(Text, nullable=True, comment="区域描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    parent = relationship("Region", remote_side=[id], back_populates="children")
    children = relationship("Region", back_populates="parent")
    schools = relationship("School", back_populates="region")


class School(Base):
    """学校模型"""
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="学校名称")
    code = Column(String(50), unique=True, nullable=False, comment="学校编码")
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, comment="所属区域ID")
    school_type = Column(String(50), nullable=False, comment="学校类型：小学、初中、高中、大学等")
    address = Column(String(500), nullable=True, comment="学校地址")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="邮箱")
    principal = Column(String(50), nullable=True, comment="校长姓名")
    is_active = Column(Boolean, default=True, comment="是否激活")
    description = Column(Text, nullable=True, comment="学校描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    region = relationship("Region", back_populates="schools")
    users = relationship("User", back_populates="school")
