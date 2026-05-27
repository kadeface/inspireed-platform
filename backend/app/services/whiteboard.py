"""
课堂白板：文档状态、操作校验与应用
"""

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session_group import SessionGroupMember
from app.models.whiteboard_state import WhiteboardState


def default_document() -> Dict[str, Any]:
    return {
        "version": 0,
        "mode": "setup",
        "zones": [],
        "elements": [],
    }


def _document_copy(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return deepcopy(raw)
    return default_document()


def _point_in_rect(px: float, py: float, rect: Dict[str, float]) -> bool:
    return (
        px >= rect["x"]
        and px <= rect["x"] + rect["w"]
        and py >= rect["y"]
        and py <= rect["y"] + rect["h"]
    )


def _element_center(el: Dict[str, Any]) -> Tuple[float, float]:
    if el.get("type") == "sticky":
        w = el.get("w") or 160
        h = el.get("h") or 110
        return el["x"] + w / 2, el["y"] + h / 2
    if el.get("type") == "stroke":
        pts = el.get("points") or []
        if not pts:
            return 0.0, 0.0
        xs = [p["x"] for p in pts]
        ys = [p["y"] for p in pts]
        return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return 0.0, 0.0


def _zone_for_group(doc: Dict[str, Any], group_index: int) -> Optional[Dict[str, Any]]:
    for z in doc.get("zones") or []:
        if z.get("groupIndex") == group_index:
            return z
    return None


def _geometry_in_zone(el: Dict[str, Any], zone: Dict[str, Any]) -> bool:
    cx, cy = _element_center(el)
    return _point_in_rect(cx, cy, zone["rect"])


def _has_connector_between(
    doc: Dict[str, Any], from_id: str, to_id: str, exclude_id: Optional[str] = None
) -> bool:
    for e in doc.get("elements") or []:
        if e.get("type") != "connector":
            continue
        if exclude_id and e.get("id") == exclude_id:
            continue
        a, b = e.get("fromId"), e.get("toId")
        if (a == from_id and b == to_id) or (a == to_id and b == from_id):
            return True
    return False


async def get_or_create_state(
    db: AsyncSession, session_id: int, cell_id: int, seed: Optional[Dict[str, Any]] = None
) -> WhiteboardState:
    result = await db.execute(
        select(WhiteboardState).where(
            and_(
                WhiteboardState.session_id == session_id,
                WhiteboardState.cell_id == cell_id,
            )
        )
    )
    row = result.scalar_one_or_none()
    if row:
        return row
    doc = deepcopy(seed) if seed else default_document()
    row = WhiteboardState(
        session_id=session_id,
        cell_id=cell_id,
        document=doc,
        version=0,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def get_member_group_index(
    db: AsyncSession, session_id: int, user_id: int
) -> Optional[int]:
    result = await db.execute(
        select(SessionGroupMember.group_index).where(
            and_(
                SessionGroupMember.session_id == session_id,
                SessionGroupMember.user_id == user_id,
            )
        )
    )
    return result.scalar_one_or_none()


def apply_op(doc: Dict[str, Any], op: Dict[str, Any]) -> None:
    action = op.get("action")
    if action == "zone.add":
        zone = op.get("zone")
        if zone:
            doc.setdefault("zones", []).append(zone)
        return
    if action == "zone.update":
        zone = op.get("zone")
        if not zone:
            return
        for i, z in enumerate(doc.get("zones") or []):
            if z.get("id") == zone.get("id"):
                doc["zones"][i] = {**z, **zone}
                break
        return
    if action == "zone.delete":
        zid = op.get("zoneId")
        doc["zones"] = [z for z in doc.get("zones") or [] if z.get("id") != zid]
        return

    el = op.get("element")
    if not el:
        return
    elements: List[Dict[str, Any]] = doc.setdefault("elements", [])
    if action == "add":
        elements.append(el)
    elif action == "update":
        for i, e in enumerate(elements):
            if e.get("id") == el.get("id"):
                elements[i] = {**e, **el}
                break
    elif action == "delete":
        eid = el.get("id") or op.get("elementId")
        doc["elements"] = [e for e in elements if e.get("id") != eid]
        doc["elements"] = [
            e
            for e in doc["elements"]
            if not (
                e.get("type") == "connector"
                and (e.get("fromId") == eid or e.get("toId") == eid)
            )
        ]


def validate_op(
    doc: Dict[str, Any],
    op: Dict[str, Any],
    *,
    is_teacher: bool,
    group_index: Optional[int],
) -> Optional[str]:
    mode = doc.get("mode", "setup")
    if mode == "locked":
        return "白板已锁定"

    action = op.get("action") or ""

    if action.startswith("zone."):
        if not is_teacher:
            return "仅教师可修改小组区域"
        return None

    if is_teacher:
        return None

    if mode != "collaborate":
        return "当前未开启协作模式"

    if group_index is None:
        return "未分配小组"

    zone = _zone_for_group(doc, group_index)
    if not zone:
        return "未找到本组区域"
    if zone.get("locked"):
        return "本组区域已锁定"

    el = op.get("element") or {}
    if el.get("groupIndex") not in (None, group_index):
        return "无权操作其他小组内容"

    check_el = el
    if action == "delete":
        eid = el.get("id") or op.get("elementId")
        found = None
        for e in doc.get("elements") or []:
            if e.get("id") == eid:
                found = e
                break
        if not found:
            return "元素不存在"
        check_el = found
        if check_el.get("groupIndex") not in (None, group_index):
            return "无权删除其他小组内容"
    elif action == "update":
        found = None
        for e in doc.get("elements") or []:
            if e.get("id") == el.get("id"):
                found = e
                break
        if not found:
            return "元素不存在"
        if found.get("groupIndex") not in (None, group_index):
            return "无权修改其他小组内容"
        check_el = {**found, **el}

    if check_el.get("type") == "connector":
        if action == "add":
            fid, tid = check_el.get("fromId"), check_el.get("toId")
            if fid and tid and _has_connector_between(doc, str(fid), str(tid)):
                return "这两个便签已经连过线了"
        return None

    if check_el and not _geometry_in_zone(check_el, zone):
        return "内容须在本组区域内"

    return None


async def process_whiteboard_op(
    db: AsyncSession,
    session_id: int,
    cell_id: int,
    op: Dict[str, Any],
    *,
    user_id: int,
    is_teacher: bool,
    seed: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    state = await get_or_create_state(db, session_id, cell_id, seed)
    doc = _document_copy(state.document)
    group_index = None if is_teacher else await get_member_group_index(db, session_id, user_id)

    err = validate_op(doc, op, is_teacher=is_teacher, group_index=group_index)
    if err:
        return None, err

    apply_op(doc, op)
    doc["version"] = int(doc.get("version") or 0) + 1
    state.document = doc  # type: ignore[assignment]
    state.version = int(state.version or 0) + 1  # type: ignore[assignment]
    state.updated_at = datetime.utcnow()  # type: ignore[assignment]
    await db.commit()
    await db.refresh(state)

    return {
        "cell_id": cell_id,
        "op": op,
        "version": state.version,
        "document_version": doc["version"],
        "actor": {
            "user_id": user_id,
            "role": "teacher" if is_teacher else "student",
            "group_index": group_index,
        },
    }, None


async def set_whiteboard_mode(
    db: AsyncSession,
    session_id: int,
    cell_id: int,
    mode: str,
) -> Dict[str, Any]:
    state = await get_or_create_state(db, session_id, cell_id)
    doc = _document_copy(state.document)
    doc["mode"] = mode
    doc["version"] = int(doc.get("version") or 0) + 1
    state.document = doc  # type: ignore[assignment]
    state.version = int(state.version or 0) + 1  # type: ignore[assignment]
    await db.commit()
    await db.refresh(state)
    return {"cell_id": cell_id, "mode": mode, "version": state.version}
