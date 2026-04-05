"""
质量监测报告 Excel 导入服务

支持小学（三率+四五六）、初中（四率+七八九）两种表结构
"""

import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MonitoringReport, MonitoringReportSchool, School

logger = logging.getLogger(__name__)


class MonitoringReportImportError(Exception):
    """质量监测报告导入错误"""
    pass


def _safe_float(v: Any) -> Optional[float]:
    if v is None or v == "" or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_int(v: Any) -> Optional[int]:
    if v is None or v == "" or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _safe_str(v: Any) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip()


def _detect_data_start_row(df: pd.DataFrame, report_type: str) -> int:
    """检测数据起始行：跳过合并表头，找到第一个包含学校名称的行"""
    for i in range(min(5, len(df))):
        row = df.iloc[i]
        if len(row) < 3:
            continue
        # 学校名称通常在列1或列2，且为字符串
        v1 = _safe_str(row.iloc[1]) if len(row) > 1 else ""
        v2 = _safe_str(row.iloc[2]) if len(row) > 2 else ""
        # 若列2像学校名（含"中学""小学""学校"等）或列1/2非纯数字，视为数据行
        if v2 and ("中学" in v2 or "小学" in v2 or "学校" in v2):
            return i
        if v1 and ("中学" in v1 or "小学" in v1 or "学校" in v1):
            return i
    return 1


async def parse_and_import(
    db: AsyncSession,
    file_path: str,
    report_type: str,
    name: str,
    academic_year: str,
    semester_type: str,
    region_id: Optional[int],
    created_by: int,
) -> MonitoringReport:
    """
    解析 Excel 并导入质量监测报告

    Args:
        db: 数据库会话
        file_path: Excel 文件路径（支持 .xlsx / .xls）
        report_type: primary | junior_high
        name: 报告名称
        academic_year: 学年 如 2025-2026
        semester_type: up | down
        region_id: 区县ID
        created_by: 创建人ID

    Returns:
        创建的 MonitoringReport
    """
    ext = Path(file_path).suffix.lower()
    if ext == ".xlsx":
        df = pd.read_excel(file_path, header=None, engine="openpyxl")
    elif ext == ".xls":
        try:
            df = pd.read_excel(file_path, header=None, engine="xlrd")
        except Exception:
            df = pd.read_excel(file_path, header=None)  # pandas 默认引擎
    else:
        raise MonitoringReportImportError(f"不支持的文件格式: {ext}，请使用 .xlsx 或 .xls")

    if df.empty or len(df) < 2:
        raise MonitoringReportImportError("Excel 文件为空或数据不足")

    # 确定数据起始行（跳过表头，可能有合并）
    data_start = _detect_data_start_row(df, report_type)
    if report_type == "primary":
        rows = _parse_primary_school_rows(df, data_start)
    else:
        # 初中表：自动检测简化版（每年级仅得分+排名）或完整版（一分四率）
        first_row = df.iloc[data_start] if len(df) > data_start else []
        non_null_count = sum(1 for v in first_row if pd.notna(v) and str(v).strip()) if len(first_row) else 0
        if non_null_count > 0 and non_null_count < 25:
            rows = _parse_junior_high_rows_simplified(df, data_start)
        else:
            rows = _parse_junior_high_rows(df, data_start)

    if not rows:
        raise MonitoringReportImportError("未能解析到有效数据行")

    report = MonitoringReport(
        name=name,
        report_type=report_type,
        academic_year=academic_year,
        semester_type=semester_type,
        region_id=region_id,
        source_file=Path(file_path).name,
        created_by=created_by,
    )
    db.add(report)
    await db.flush()

    # 尝试匹配学校
    school_cache: Dict[str, int] = {}

    for idx, row_data in enumerate(rows):
        school_name = row_data.get("school_name") or ""
        school_code = row_data.get("school_code") or ""
        if not school_name and not school_code:
            continue

        school_id = None
        if school_code and school_code in school_cache:
            school_id = school_cache[school_code]
        elif school_name or school_code:
            from sqlalchemy import select, or_
            q = select(School.id)
            if school_code and school_name:
                q = q.where(or_(School.code == school_code, School.name == school_name))
            elif school_code:
                q = q.where(School.code == school_code)
            else:
                q = q.where(School.name == school_name)
            r = await db.execute(q.limit(1))
            sid = r.scalar_one_or_none()
            if sid:
                school_id = sid
                if school_code:
                    school_cache[school_code] = school_id

        _valid = {
            "g9_one_point", "g9_excellent_rate", "g9_good_rate", "g9_pass_rate", "g9_low_rate",
            "g9_comprehensive", "g9_score", "g9_rank", "g8_one_point", "g8_excellent_rate", "g8_good_rate",
            "g8_pass_rate", "g8_low_rate", "g8_comprehensive", "g8_score", "g8_rank",
            "g7_one_point", "g7_excellent_rate", "g7_good_rate", "g7_pass_rate", "g7_low_rate",
            "g7_comprehensive", "g7_score", "g7_rank",
            "g789_one_point", "g789_excellent_rate", "g789_good_rate", "g789_pass_rate",
            "g789_low_rate", "g789_total_score", "g789_rank",
            "g9_value_added_score", "g9_value_added_rank", "g8_value_added_score", "g8_value_added_rank",
            "g7_value_added_score", "g7_value_added_rank", "g789_value_added_score", "g789_value_added_rank",
            "g6_one_point", "g6_excellent_rate", "g6_good_rate", "g6_pass_rate",
            "g6_comprehensive", "g6_score", "g6_rank", "g5_one_point", "g5_excellent_rate", "g5_good_rate",
            "g5_pass_rate", "g5_comprehensive", "g5_score", "g5_rank",
            "g4_one_point", "g4_excellent_rate", "g4_good_rate", "g4_pass_rate",
            "g4_comprehensive", "g4_score", "g4_rank",
            "g456_one_point", "g456_excellent_rate", "g456_good_rate", "g456_pass_rate",
            "g456_total_score", "g456_rank",
            "g6_value_added_score", "g6_value_added_rank", "g5_value_added_score", "g5_value_added_rank",
            "g4_value_added_score", "g4_value_added_rank", "g456_value_added_score", "g456_value_added_rank",
        }
        data = {k: v for k, v in row_data.items() if k in _valid}
        school_row = MonitoringReportSchool(
            report_id=report.id,
            school_code=school_code or None,
            school_id=school_id,
            school_name=school_name or "未知",
            display_order=idx,
            remarks=row_data.get("remarks"),
            **data,
        )
        db.add(school_row)

    await db.commit()
    await db.refresh(report)
    logger.info(f"导入质量监测报告: {report.id}, {len(rows)} 所学校")
    return report


def _parse_primary_school_rows(df: pd.DataFrame, data_start: int) -> List[Dict[str, Any]]:
    """
    解析小学表：学校/代码/学校名称 | 六年级一分三率综合得分+排名 | 五年级... | 四年级... | 3级... | 增值...
    列顺序参考：代码(0), 学校名称(1), 六年级一分(2)三率(3)综合(4)得分(5), 六年级排名(6), 五年级..., 四年级..., 3级..., 增值...
    """
    rows = []
    for i in range(data_start, len(df)):
        row = df.iloc[i]
        if len(row) < 3:
            continue
        code = _safe_str(row.iloc[0]) if len(row) > 0 else ""
        school_name = _safe_str(row.iloc[1]) if len(row) > 1 else _safe_str(row.iloc[0])
        if not school_name and not code:
            continue
        r = lambda idx: row.iloc[idx] if idx < len(row) else None
        rows.append({
            "school_name": school_name or code,
            "school_code": code or None,
            "g6_one_point": _safe_float(r(2)), "g6_excellent_rate": _safe_float(r(3)),
            "g6_good_rate": None, "g6_pass_rate": None,
            "g6_comprehensive": _safe_float(r(4)), "g6_score": _safe_float(r(5)),
            "g6_rank": _safe_int(r(6)),
            "g5_one_point": _safe_float(r(7)), "g5_excellent_rate": _safe_float(r(8)),
            "g5_good_rate": None, "g5_pass_rate": None,
            "g5_comprehensive": _safe_float(r(9)), "g5_score": _safe_float(r(10)),
            "g5_rank": _safe_int(r(11)),
            "g4_one_point": _safe_float(r(12)), "g4_excellent_rate": _safe_float(r(13)),
            "g4_good_rate": None, "g4_pass_rate": None,
            "g4_comprehensive": _safe_float(r(14)), "g4_score": _safe_float(r(15)),
            "g4_rank": _safe_int(r(16)),
            "g456_one_point": _safe_float(r(17)), "g456_excellent_rate": _safe_float(r(18)),
            "g456_good_rate": None, "g456_pass_rate": None,
            "g456_total_score": _safe_float(r(19)), "g456_rank": _safe_int(r(20)),
            "g6_value_added_score": _safe_float(r(21)), "g6_value_added_rank": _safe_int(r(22)),
            "g5_value_added_score": _safe_float(r(23)), "g5_value_added_rank": _safe_int(r(24)),
            "g4_value_added_score": _safe_float(r(25)), "g4_value_added_rank": _safe_int(r(26)),
            "g456_value_added_score": _safe_float(r(27)), "g456_value_added_rank": _safe_int(r(28)),
            "remarks": _safe_str(r(min(29, len(row) - 1))),
        })
    return rows


def _parse_junior_high_rows_simplified(df: pd.DataFrame, data_start: int) -> List[Dict[str, Any]]:
    """
    解析初中表（按实际表头结构）：
    学校代码(0), 学校名称(1),
    一分四率综合: 九年级得分(2)排名(3), 八年级得分(4)排名(5), 七年级得分(6)排名(7),
                 3级合计得分(8)排名(9),
    增值评价综合: 九年级得分(10)排名(11), 八年级得分(12)排名(13), 七年级得分(14)排名(15),
                 3级合计得分(16)排名(17),
    备注(18)
    """
    rows = []
    for i in range(data_start, len(df)):
        row = df.iloc[i]
        if len(row) < 5:
            continue
        r = lambda idx: row.iloc[idx] if idx < len(row) else None
        school_code = _safe_str(r(0)) or None
        school_name = _safe_str(r(1))
        if not school_name and not school_code:
            continue
        rows.append({
            "school_name": school_name or (school_code or "未知"),
            "school_code": school_code,
            "g9_score": _safe_float(r(2)),
            "g9_rank": _safe_int(r(3)),
            "g8_score": _safe_float(r(4)),
            "g8_rank": _safe_int(r(5)),
            "g7_score": _safe_float(r(6)),
            "g7_rank": _safe_int(r(7)),
            "g789_total_score": _safe_float(r(8)),
            "g789_rank": _safe_int(r(9)),
            "g9_value_added_score": _safe_float(r(10)),
            "g9_value_added_rank": _safe_int(r(11)),
            "g8_value_added_score": _safe_float(r(12)),
            "g8_value_added_rank": _safe_int(r(13)),
            "g7_value_added_score": _safe_float(r(14)),
            "g7_value_added_rank": _safe_int(r(15)),
            "g789_value_added_score": _safe_float(r(16)),
            "g789_value_added_rank": _safe_int(r(17)),
            "remarks": _safe_str(r(18)) if len(row) > 18 else None,
        })
    return rows


def _parse_junior_high_rows(df: pd.DataFrame, data_start: int) -> List[Dict[str, Any]]:
    """解析初中表（完整版）：学校、代码、学校名称 | 九年级一分四率综合得分排名 | ..."""
    rows = []
    for i in range(data_start, len(df)):
        row = df.iloc[i]
        if len(row) < 5:
            continue
        school_name = _safe_str(row.get(2, ""))
        school_code = _safe_str(row.get(1, ""))
        if not school_name and not school_code:
            continue
        rows.append({
            "school_name": school_name or school_code,
            "school_code": school_code or None,
            "g9_one_point": _safe_float(row.get(3)) if len(row) > 3 else None,
            "g9_excellent_rate": _safe_float(row.get(4)) if len(row) > 4 else None,
            "g9_good_rate": _safe_float(row.get(5)) if len(row) > 5 else None,
            "g9_pass_rate": _safe_float(row.get(6)) if len(row) > 6 else None,
            "g9_low_rate": _safe_float(row.get(7)) if len(row) > 7 else None,
            "g9_comprehensive": _safe_float(row.get(8)) if len(row) > 8 else None,
            "g9_score": _safe_float(row.get(9)) if len(row) > 9 else None,
            "g9_rank": _safe_int(row.get(13)) if len(row) > 13 else None,
            "g8_one_point": _safe_float(row.get(14)) if len(row) > 14 else None,
            "g8_excellent_rate": _safe_float(row.get(15)) if len(row) > 15 else None,
            "g8_good_rate": _safe_float(row.get(16)) if len(row) > 16 else None,
            "g8_pass_rate": _safe_float(row.get(17)) if len(row) > 17 else None,
            "g8_low_rate": _safe_float(row.get(18)) if len(row) > 18 else None,
            "g8_comprehensive": _safe_float(row.get(19)) if len(row) > 19 else None,
            "g8_score": _safe_float(row.get(20)) if len(row) > 20 else None,
            "g8_rank": _safe_int(row.get(24)) if len(row) > 24 else None,
            "g7_one_point": _safe_float(row.get(25)) if len(row) > 25 else None,
            "g7_excellent_rate": _safe_float(row.get(26)) if len(row) > 26 else None,
            "g7_good_rate": _safe_float(row.get(27)) if len(row) > 27 else None,
            "g7_pass_rate": _safe_float(row.get(28)) if len(row) > 28 else None,
            "g7_low_rate": _safe_float(row.get(29)) if len(row) > 29 else None,
            "g7_comprehensive": _safe_float(row.get(30)) if len(row) > 30 else None,
            "g7_score": _safe_float(row.get(31)) if len(row) > 31 else None,
            "g7_rank": _safe_int(row.get(35)) if len(row) > 35 else None,
            "g789_one_point": _safe_float(row.get(36)) if len(row) > 36 else None,
            "g789_excellent_rate": _safe_float(row.get(37)) if len(row) > 37 else None,
            "g789_good_rate": _safe_float(row.get(38)) if len(row) > 38 else None,
            "g789_pass_rate": _safe_float(row.get(39)) if len(row) > 39 else None,
            "g789_low_rate": _safe_float(row.get(40)) if len(row) > 40 else None,
            "g789_total_score": _safe_float(row.get(41)) if len(row) > 41 else None,
            "g789_rank": _safe_int(row.get(42)) if len(row) > 42 else None,
            "g9_value_added_score": _safe_float(row.get(43)) if len(row) > 43 else None,
            "g9_value_added_rank": _safe_int(row.get(44)) if len(row) > 44 else None,
            "g8_value_added_score": _safe_float(row.get(45)) if len(row) > 45 else None,
            "g8_value_added_rank": _safe_int(row.get(46)) if len(row) > 46 else None,
            "g7_value_added_score": _safe_float(row.get(47)) if len(row) > 47 else None,
            "g7_value_added_rank": _safe_int(row.get(48)) if len(row) > 48 else None,
            "g789_value_added_score": _safe_float(row.get(49)) if len(row) > 49 else None,
            "g789_value_added_rank": _safe_int(row.get(50)) if len(row) > 50 else None,
            "remarks": _safe_str(row.get(len(row) - 1)) if len(row) > 50 else None,
        })
    return rows
