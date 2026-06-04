"""
站点访问统计（公开页脚展示）
"""

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Integer

from app.core.database import Base


class SiteStatistics(Base):
    """全站访问量计数（单行记录 id=1）"""

    __tablename__ = "site_statistics"

    id = Column(Integer, primary_key=True)
    total_visits = Column(Integer, nullable=False, default=0, comment="累计访问量")
    today_visits = Column(Integer, nullable=False, default=0, comment="今日访问量")
    today_date = Column(Date, nullable=True, comment="今日计数对应日期")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
