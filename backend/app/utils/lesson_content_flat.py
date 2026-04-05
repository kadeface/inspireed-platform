"""
与 frontend/src/utils/lessonContent.ts 对齐：从 Lesson.content 扁平化出所有 cell 字典。
用于访客「全课模块目录」等场景；数据库 cells 表可能只同步了部分单元（如活动）。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

DEFAULT_SECTION_NAMES: Sequence[str] = (
    "教学目标、教学重点难点、学生学情分析",
    "教学过程",
    "课堂练习",
    "课程资源",
    "反思总结",
)

TEACHING_PROCESS_ORDER = 1


def _empty_default_sections() -> List[Dict[str, Any]]:
    return [
        {
            "id": f"sec-default-{i}",
            "name": name,
            "type": "default",
            "order": i,
            "is_collapsed": False,
            "cells": [],
        }
        for i, name in enumerate(DEFAULT_SECTION_NAMES)
    ]


def _is_content_with_sections(content: Any) -> bool:
    return isinstance(content, dict) and isinstance(content.get("sections"), list)


def normalize_content_to_sections(content: Optional[Any]) -> List[Dict[str, Any]]:
    """对应 normalizeContentToSections。"""
    if not content:
        return _empty_default_sections()

    if _is_content_with_sections(content):
        raw_sections = list(content.get("sections") or [])
        default_map: Dict[str, Dict[str, Any]] = {
            name: {"order": i, "filled": False} for i, name in enumerate(DEFAULT_SECTION_NAMES)
        }
        result: List[Dict[str, Any]] = []
        seen_ids: set[str] = set()

        for s in raw_sections:
            if not isinstance(s, dict):
                continue
            sec = {**s, "cells": s.get("cells") or []}
            sid = sec.get("id")
            if sid is not None:
                seen_ids.add(str(sid))
            result.append(sec)
            name = sec.get("name")
            if isinstance(name, str) and name in default_map:
                default_map[name]["filled"] = True

        for i, name in enumerate(DEFAULT_SECTION_NAMES):
            if default_map[name]["filled"]:
                continue
            sec_id = f"sec-default-{i}"
            if sec_id in seen_ids:
                continue
            result.append(
                {
                    "id": sec_id,
                    "name": name,
                    "type": "default",
                    "order": i,
                    "is_collapsed": False,
                    "cells": [],
                }
            )

        result.sort(key=lambda x: (x.get("order") if isinstance(x.get("order"), int) else 0))
        return result

    # 旧格式：平铺 Cell[]
    if not isinstance(content, list):
        return _empty_default_sections()

    sections = _empty_default_sections()
    teaching = next((s for s in sections if s.get("order") == TEACHING_PROCESS_ORDER), None)
    if teaching is not None:
        teaching["cells"] = []
        for i, c in enumerate(content):
            if isinstance(c, dict):
                merged = {**c, "order": i}
                teaching["cells"].append(merged)
    return sections


def sections_to_flat_cells(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """对应 sectionsToFlatCells。"""
    out: List[Dict[str, Any]] = []
    for s in sections:
        cells = s.get("cells") if isinstance(s, dict) else None
        if isinstance(cells, list):
            for c in cells:
                if isinstance(c, dict):
                    out.append(c)
    return out


def flatten_lesson_content_cells(content: Optional[Any]) -> List[Dict[str, Any]]:
    """Lesson.content → 与教师端 lessonContentCells 顺序一致的 cell  dict 列表。"""
    sections = normalize_content_to_sections(content)
    return sections_to_flat_cells(sections)


def build_json_cells_by_effective_order(content: Optional[Any]) -> Dict[int, Dict[str, Any]]:
    """
    教案 JSON 中每个 cell 的有效 order → 原始 dict（与导播台 cellOrder 一致）。
    同一 order 多处出现时保留先遍历到的（与 lesson_content_to_guest_outline 一致）。
    """
    flat = flatten_lesson_content_cells(content)
    by_order: Dict[int, Dict[str, Any]] = {}
    for idx, c in enumerate(flat):
        if not isinstance(c, dict):
            continue
        ord_raw = c.get("order")
        if ord_raw is None:
            order_val = idx
        else:
            try:
                order_val = int(ord_raw)
            except (TypeError, ValueError):
                order_val = idx
        if order_val not in by_order:
            by_order[order_val] = c
    return by_order


def guest_payload_from_lesson_cell_dict(c: Dict[str, Any], display_order: int) -> Dict[str, Any]:
    """将教案 JSON 中的 cell 转为 guest_get_session_cells 中单条记录形状。"""
    raw_type = c.get("type") or c.get("cell_type") or "TEXT"
    if hasattr(raw_type, "value"):
        raw_type = raw_type.value
    cell_type = str(raw_type).upper() if raw_type else "TEXT"

    cid = c.get("id")
    guest_id: Any
    if isinstance(cid, bool):
        guest_id = f"lesson-{display_order}"
    elif isinstance(cid, int):
        guest_id = cid
    elif isinstance(cid, float) and cid == int(cid):
        guest_id = int(cid)
    elif isinstance(cid, str) and cid.isdigit():
        guest_id = int(cid)
    else:
        guest_id = f"lesson-{display_order}"

    return {
        "id": guest_id,
        "cell_type": cell_type,
        "title": c.get("title"),
        "content": c.get("content"),
        "config": c.get("config"),
        "order": display_order,
    }


def lesson_content_to_guest_outline(content: Optional[Any]) -> List[Dict[str, Any]]:
    """
    生成访客用的轻量目录（order / title / cell_type / outline_id）。
    order：与导播台一致，优先 JSON 的 order，否则为在扁平列表中的下标。
    """
    flat = flatten_lesson_content_cells(content)
    outline: List[Dict[str, Any]] = []
    for idx, c in enumerate(flat):
        raw_type = c.get("type") or c.get("cell_type") or "TEXT"
        if hasattr(raw_type, "value"):
            raw_type = raw_type.value
        cell_type = str(raw_type).upper() if raw_type else "TEXT"

        ord_raw = c.get("order")
        if ord_raw is None:
            order_val: Optional[int] = idx
        else:
            try:
                order_val = int(ord_raw)
            except (TypeError, ValueError):
                order_val = idx

        title = str(c.get("title") or "").strip()
        cid = c.get("id")
        outline_id = cid if cid is not None else f"flat-{idx}"

        outline.append(
            {
                "id": outline_id,
                "order": order_val,
                "title": title,
                "cell_type": cell_type,
            }
        )
    return outline
