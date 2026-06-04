"""
公开站点统计（页脚访客统计，无需登录）
"""

from datetime import date
from typing import Any, Optional, cast

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.site_statistics import SiteStatistics

router = APIRouter()

SITE_STATS_ROW_ID = 1


class SiteVisitorStatsResponse(BaseModel):
    total_visits: int = Field(description="累计访问量")
    today_visits: int = Field(description="今日访问量")


async def _get_or_create_stats(db: AsyncSession) -> SiteStatistics:
    row = await db.get(SiteStatistics, SITE_STATS_ROW_ID)
    if row is None:
        row = SiteStatistics(
            id=SITE_STATS_ROW_ID,
            total_visits=0,
            today_visits=0,
            today_date=None,
        )
        db.add(row)
        await db.flush()
    return row


def _reset_today_if_needed(row: SiteStatistics, today: date) -> None:
    stored = cast(Optional[date], row.today_date)
    if stored != today:
        setattr(row, "today_visits", 0)
        setattr(row, "today_date", today)


@router.get("/visitors/stats", response_model=SiteVisitorStatsResponse)
async def get_visitor_stats(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """获取访客统计（公开）"""
    row = await _get_or_create_stats(db)
    today = date.today()
    _reset_today_if_needed(row, today)
    await db.commit()
    return SiteVisitorStatsResponse(
        total_visits=cast(int, row.total_visits),
        today_visits=cast(int, row.today_visits),
    )


@router.post("/visitors/record", response_model=SiteVisitorStatsResponse)
async def record_visitor(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """记录一次访问（公开；客户端应在同一会话/自然日内去重）"""
    row = await _get_or_create_stats(db)
    today = date.today()
    _reset_today_if_needed(row, today)

    setattr(row, "total_visits", cast(int, row.total_visits) + 1)
    setattr(row, "today_visits", cast(int, row.today_visits) + 1)
    setattr(row, "today_date", today)

    await db.commit()
    return SiteVisitorStatsResponse(
        total_visits=cast(int, row.total_visits),
        today_visits=cast(int, row.today_visits),
    )
