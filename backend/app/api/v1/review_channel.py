"""
作品评审通道（无数据库 MVP）
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Optional

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.config import settings

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

router = APIRouter()


REVIEW_DATA_ROOT = Path(settings.UPLOAD_DIR) / "review-data" / "activities"


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _front_base_url() -> str:
    base = _normalize_str(getattr(settings, "REVIEW_CHANNEL_FRONTEND_BASE_URL", ""))
    return base.rstrip("/")


def _build_front_link(activity_id: str, role: str, token: str, request: Optional[Request] = None) -> str:
    base = _front_base_url()
    role_path = "coordinator" if role == "coordinator" else "judge"
    if base:
        return f"{base}/review-channel/{role_path}?activity_id={activity_id}&token={token}"
    # Auto-detect frontend URL from request (for development)
    if request:
        scheme = request.url.scheme
        host = request.headers.get("host", "")
        # Replace backend port with frontend port for development
        if ":8000" in host:
            host = host.replace(":8000", ":5173")
        elif host.endswith(":80") or host.endswith(":443"):
            # In production, use the same host
            pass
        return f"{scheme}://{host}/review-channel/{role_path}?activity_id={activity_id}&token={token}"
    return f"/review-channel/{role_path}?activity_id={activity_id}&token={token}"


def _activity_dir(activity_id: str) -> Path:
    return REVIEW_DATA_ROOT / activity_id


def _paths(activity_id: str) -> dict[str, Path]:
    base = _activity_dir(activity_id)
    return {
        "base": base,
        "meta": base / "meta.json",
        "works": base / "works.jsonl",
        "assignments": base / "assignments.json",
        "tokens": base / "tokens.json",
        "scores": base / "scores.log.jsonl",
        "summary": base / "snapshots" / "summary.json",
        "progress": base / "snapshots" / "progress.json",
        "exports": base / "exports",
        "lock": base / "locks" / "scores.lock",
    }


def _ensure_activity_exists(activity_id: str) -> dict[str, Path]:
    p = _paths(activity_id)
    if not p["base"].exists():
        raise HTTPException(status_code=404, detail="评审活动不存在")
    return p


def _json_load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _json_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    temp.replace(path)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


@contextmanager
def _file_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        if fcntl is not None:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _normalize_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and pd.isna(v):
        return ""
    return str(v).strip()


def _load_works(activity_id: str) -> list[dict[str, Any]]:
    p = _ensure_activity_exists(activity_id)
    return _read_jsonl(p["works"])


def _scope_match(work: dict[str, Any], scopes: list[dict[str, str]]) -> bool:
    if not scopes:
        return False
    for scope in scopes:
        if (
            scope.get("grade_band") == work.get("grade_band")
            and scope.get("subject") == work.get("subject")
        ):
            return True
    return False


def _parse_cell_people(cell: str) -> list[dict[str, str]]:
    value = _normalize_str(cell)
    if not value:
        return []
    chunks = [x.strip() for x in value.replace("；", ";").replace("，", ",").split(";") if x.strip()]
    people: list[dict[str, str]] = []
    for chunk in chunks:
        parts = [x.strip() for x in chunk.split(",") if x.strip()]
        if not parts:
            continue
        item: dict[str, str] = {"name": parts[0]}
        if len(parts) >= 2:
            item["contact"] = parts[1]
        people.append(item)
    return people


def _parse_assignment_key(key: str) -> Optional[tuple[str, str, Literal["judge", "coordinator"]]]:
    s = _normalize_str(key)
    if not s:
        return None
    if s.endswith("教研员"):
        role: Literal["judge", "coordinator"] = "coordinator"
        core = s[:-3]
    elif "评委" in s:
        role = "judge"
        idx = s.index("评委")
        core = s[:idx]
    else:
        return None

    grade_candidates = ["小学", "初中", "高中", "中职", "高职"]
    grade = next((g for g in grade_candidates if core.startswith(g)), "")
    if not grade:
        return None
    subject = core[len(grade) :].strip()
    if not subject:
        return None
    return grade, subject, role


def _rules_from_column_map(column_map: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    rules: list[dict[str, str]] = []
    warnings: list[str] = []
    for key, value in column_map.items():
        parsed = _parse_assignment_key(key)
        if parsed is None:
            continue
        grade_band, subject, role = parsed
        people = _parse_cell_people(_normalize_str(value))
        if not people:
            continue
        for person in people:
            name = person.get("name", "").strip()
            if not name:
                continue
            rules.append(
                {
                    "grade_band": grade_band,
                    "subject": subject,
                    "role": role,
                    "name": name,
                    "contact": person.get("contact", ""),
                }
            )
    if not rules:
        warnings.append("未解析到任何有效分配规则")
    return rules, warnings


def _load_session(token: str, activity_id: Optional[str] = None) -> dict[str, Any]:
    if not token:
        raise HTTPException(status_code=401, detail="缺少访问令牌")
    token_h = _token_hash(token)
    if not REVIEW_DATA_ROOT.exists():
        raise HTTPException(status_code=401, detail="令牌无效")

    activity_dirs = [(_activity_dir(activity_id), activity_id)] if activity_id else [
        (p, p.name) for p in REVIEW_DATA_ROOT.iterdir() if p.is_dir()
    ]
    for base, aid in activity_dirs:
        tokens_path = base / "tokens.json"
        tokens = _json_load(tokens_path, default=[])
        for item in tokens:
            if item.get("token_hash") != token_h:
                continue
            if item.get("revoked"):
                raise HTTPException(status_code=401, detail="令牌已失效")
            expires_at = item.get("expires_at")
            if expires_at:
                try:
                    exp = datetime.fromisoformat(expires_at)
                    if datetime.now().astimezone() > exp:
                        raise HTTPException(status_code=401, detail="令牌已过期")
                except ValueError:
                    pass
            if activity_id and aid != activity_id:
                raise HTTPException(status_code=403, detail="令牌与活动不匹配")
            return {
                "activity_id": aid,
                "name": item.get("name"),
                "role": item.get("role"),
                "scopes": item.get("scopes", []),
            }
    raise HTTPException(status_code=401, detail="令牌无效")


def _recompute(activity_id: str) -> dict[str, Any]:
    p = _ensure_activity_exists(activity_id)
    works = _read_jsonl(p["works"])
    events = _read_jsonl(p["scores"])

    latest_submit: dict[tuple[str, str], dict[str, Any]] = {}
    for ev in events:
        if ev.get("event") != "submit":
            continue
        key = (str(ev.get("work_id", "")), str(ev.get("judge", "")))
        if not key[0] or not key[1]:
            continue
        latest_submit[key] = ev

    by_work: dict[str, list[dict[str, Any]]] = {}
    for (work_id, _), ev in latest_submit.items():
        by_work.setdefault(work_id, []).append(ev)

    summary_rows: list[dict[str, Any]] = []
    scored_works = 0

    for work in works:
        work_id = str(work.get("work_id", ""))
        submits = by_work.get(work_id, [])
        scores = []
        for submit in submits:
            try:
                scores.append(float(submit.get("score_total")))
            except (TypeError, ValueError):
                continue
        if scores:
            scored_works += 1
            final_score: Optional[float] = round(sum(scores) / len(scores), 1)
            status_text = "已评分"
        else:
            final_score = None
            status_text = "未评分"

        summary_rows.append(
            {
                "work_id": work_id,
                "work_number": work.get("work_number"),
                "title": work.get("title"),
                "grade_band": work.get("grade_band"),
                "subject": work.get("subject"),
                "school_name": work.get("school_name"),
                "review_count": len(scores),
                "final_score": final_score,
                "status": status_text,
            }
        )

    summary_rows.sort(
        key=lambda x: (
            x.get("final_score") is None,
            -(x.get("final_score") or 0.0),
            str(x.get("work_number") or ""),
        )
    )

    progress = {
        "total_works": len(works),
        "scored_works": scored_works,
        "unscored_works": max(len(works) - scored_works, 0),
    }

    _json_dump(p["summary"], summary_rows)
    _json_dump(p["progress"], progress)
    return {"summary": summary_rows, "progress": progress}


def _extract_scopes_from_works(activity_id: str) -> set[tuple[str, str]]:
    works = _load_works(activity_id)
    return {
        (str(w.get("grade_band", "")).strip(), str(w.get("subject", "")).strip())
        for w in works
        if str(w.get("grade_band", "")).strip() and str(w.get("subject", "")).strip()
    }


def _extract_scopes_from_rules(rules: list[dict[str, Any]]) -> set[tuple[str, str]]:
    scopes: set[tuple[str, str]] = set()
    for rule in rules:
        if rule.get("role") != "judge":
            continue
        grade_band = _normalize_str(rule.get("grade_band"))
        subject = _normalize_str(rule.get("subject"))
        if grade_band and subject:
            scopes.add((grade_band, subject))
    return scopes


class ReviewActivityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    starts_at: Optional[str] = None
    ends_at: Optional[str] = None


class AssignmentRule(BaseModel):
    grade_band: str
    subject: str
    role: Literal["judge", "coordinator"]
    name: str
    contact: Optional[str] = None


class AssignmentsPayload(BaseModel):
    rules: list[AssignmentRule]


class GenerateLinksPayload(BaseModel):
    expires_at: Optional[str] = None
    regenerate: bool = False


class ScorePayload(BaseModel):
    score_total: float
    comment: str = ""


@router.post("/review-channel/activities", status_code=status.HTTP_201_CREATED)
async def create_review_activity(payload: ReviewActivityCreate) -> dict[str, Any]:
    activity_id = f"act_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    p = _paths(activity_id)
    p["base"].mkdir(parents=True, exist_ok=False)
    p["exports"].mkdir(parents=True, exist_ok=True)
    _json_dump(
        p["meta"],
        {
            "activity_id": activity_id,
            "name": payload.name.strip(),
            "description": payload.description.strip(),
            "starts_at": payload.starts_at,
            "ends_at": payload.ends_at,
            "status": "draft",
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        },
    )
    return {"activity_id": activity_id, "name": payload.name}


@router.post("/review-channel/activities/{activity_id}/works/import")
async def import_review_works(activity_id: str, file: UploadFile = File(...)) -> dict[str, Any]:
    p = _ensure_activity_exists(activity_id)
    if not file.filename:
        raise HTTPException(status_code=400, detail="必须上传 Excel 文件")
    ext = Path(file.filename).suffix.lower()
    if ext not in {".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail="仅支持 xlsx/xls 文件")

    content = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Excel 解析失败: {exc}") from exc

    required_cols = ["作品编号", "作品名", "学段", "学科", "链接地址"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"缺少必填列: {', '.join(missing)}")

    work_map: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    for i, row in df.iterrows():
        row_no = i + 2
        work_number = _normalize_str(row.get("作品编号"))
        title = _normalize_str(row.get("作品名"))
        grade_band = _normalize_str(row.get("学段"))
        subject = _normalize_str(row.get("学科"))
        url = _normalize_str(row.get("链接地址"))
        if not work_number or not title or not grade_band or not subject or not url:
            warnings.append(f"第{row_no}行存在必填字段为空，已跳过")
            continue
        if not (url.startswith("http://") or url.startswith("https://")):
            warnings.append(f"第{row_no}行链接地址非 http(s)，已跳过")
            continue

        entry = work_map.get(work_number)
        if entry is None:
            entry = {
                "work_id": f"w_{uuid.uuid4().hex[:12]}",
                "work_number": work_number,
                "title": title,
                "author_name": _normalize_str(row.get("上传者")),
                "city": _normalize_str(row.get("市")),
                "district": _normalize_str(row.get("区")),
                "school_name": _normalize_str(row.get("学校")),
                "grade_band": grade_band,
                "subject": subject,
                "chapter_text": _normalize_str(row.get("章节")),
                "attachments": [],
                "updated_at": _now_iso(),
            }
            work_map[work_number] = entry

        attachment = {
            "name": _normalize_str(row.get("附件名")),
            "format": _normalize_str(row.get("格式")),
            "url": url,
        }
        key = f"{attachment['name']}|{attachment['format']}|{attachment['url']}"
        existing_keys = {
            f"{a.get('name', '')}|{a.get('format', '')}|{a.get('url', '')}"
            for a in entry["attachments"]
        }
        if key not in existing_keys:
            entry["attachments"].append(attachment)

    with p["works"].open("w", encoding="utf-8") as f:
        for item in work_map.values():
            f.write(json.dumps(item, ensure_ascii=False) + os.linesep)

    _recompute(activity_id)
    return {
        "works_upserted": len(work_map),
        "attachments_inserted": sum(len(v["attachments"]) for v in work_map.values()),
        "warnings": warnings,
    }



@router.get("/review-channel/activities/{activity_id}/assignments")
async def get_assignments(activity_id: str) -> dict[str, Any]:
    """获取当前分配规则"""
    p = _ensure_activity_exists(activity_id)
    assignments = _json_load(p["assignments"], default={"rules": []})
    return assignments

@router.put("/review-channel/activities/{activity_id}/assignments")
async def save_assignments(activity_id: str, payload: AssignmentsPayload) -> dict[str, Any]:
    p = _ensure_activity_exists(activity_id)
    rules = [
        {
            "grade_band": r.grade_band.strip(),
            "subject": r.subject.strip(),
            "role": r.role,
            "name": r.name.strip(),
            "contact": (r.contact or "").strip(),
        }
        for r in payload.rules
        if r.name.strip()
    ]
    _json_dump(p["assignments"], {"rules": rules, "updated_at": _now_iso()})
    work_scopes = _extract_scopes_from_works(activity_id)
    assigned_scopes = _extract_scopes_from_rules(rules)
    uncovered = sorted(list(work_scopes - assigned_scopes))
    return {
        "saved": len(rules),
        "uncovered_scopes": [
            {"grade_band": grade_band, "subject": subject}
            for grade_band, subject in uncovered
        ],
    }


@router.post("/review-channel/activities/{activity_id}/assignments/from-columns")
async def save_assignments_from_columns(activity_id: str, payload: dict[str, str]) -> dict[str, Any]:
    p = _ensure_activity_exists(activity_id)
    rules, warnings = _rules_from_column_map(payload)
    _json_dump(p["assignments"], {"rules": rules, "updated_at": _now_iso()})
    work_scopes = _extract_scopes_from_works(activity_id)
    assigned_scopes = _extract_scopes_from_rules(rules)
    uncovered = sorted(list(work_scopes - assigned_scopes))
    return {
        "saved": len(rules),
        "warnings": warnings,
        "uncovered_scopes": [
            {"grade_band": grade_band, "subject": subject}
            for grade_band, subject in uncovered
        ],
    }


@router.get("/review-channel/activities/{activity_id}/assignments/template")
async def export_assignments_template(
    activity_id: str,
    max_judges_per_scope: int = Query(default=3, ge=1, le=50),
    fmt: Literal["xlsx", "csv"] = Query(default="xlsx"),
) -> FileResponse:
    p = _ensure_activity_exists(activity_id)
    columns_resp = await get_assignment_columns(activity_id, max_judges_per_scope=max_judges_per_scope)
    columns = columns_resp["columns"]
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = p["exports"] / f"assignments-template-{ts}.{fmt}"

    row: dict[str, Any] = {c: "" for c in columns}
    _write_table(file_path, [row], columns=columns, fmt=fmt)
    return FileResponse(path=file_path, filename=file_path.name)


@router.post("/review-channel/activities/{activity_id}/assignments/import-template")
async def import_assignments_template(
    activity_id: str,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    p = _ensure_activity_exists(activity_id)
    if not file.filename:
        raise HTTPException(status_code=400, detail="必须上传模板文件")
    ext = Path(file.filename).suffix.lower()
    if ext not in {".xlsx", ".xls", ".csv"}:
        raise HTTPException(status_code=400, detail="仅支持 xlsx/xls/csv 模板文件")

    content = await file.read()
    try:
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"模板解析失败: {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="模板为空，无法导入")

    merged_map: dict[str, str] = {}
    for _, row in df.iterrows():
        for col in df.columns:
            key = _normalize_str(col)
            val = _normalize_str(row.get(col))
            if not key or not val:
                continue
            if key not in merged_map:
                merged_map[key] = val
            else:
                merged_map[key] = f"{merged_map[key]};{val}"

    rules, warnings = _rules_from_column_map(merged_map)
    if not rules:
        raise HTTPException(status_code=400, detail="未解析到任何有效分配规则")
    _json_dump(p["assignments"], {"rules": rules, "updated_at": _now_iso()})
    work_scopes = _extract_scopes_from_works(activity_id)
    assigned_scopes = _extract_scopes_from_rules(rules)
    uncovered = sorted(list(work_scopes - assigned_scopes))
    return {
        "saved": len(rules),
        "warnings": warnings,
        "parsed_columns": len(merged_map),
        "uncovered_scopes": [
            {"grade_band": grade_band, "subject": subject}
            for grade_band, subject in uncovered
        ],
    }


@router.post("/review-channel/activities/{activity_id}/access-links/generate")
async def generate_access_links(activity_id: str, payload: GenerateLinksPayload, request: Request) -> dict[str, Any]:
    p = _ensure_activity_exists(activity_id)
    assignments = _json_load(p["assignments"], default={"rules": []})
    rules = assignments.get("rules", [])
    if not rules:
        raise HTTPException(status_code=400, detail="请先配置评委/教研员分配规则")

    current_tokens = _json_load(p["tokens"], default=[])
    if payload.regenerate:
        current_tokens = []

    by_person: dict[tuple[str, str], dict[str, Any]] = {}
    for r in rules:
        role = r.get("role")
        name = _normalize_str(r.get("name"))
        if role not in {"judge", "coordinator"} or not name:
            continue
        key = (name, role)
        entry = by_person.setdefault(
            key,
            {
                "name": name,
                "role": role,
                "scopes": [],
                "contact": _normalize_str(r.get("contact")),
            },
        )
        # Collect scope for both judges and coordinators
        scope = {"grade_band": _normalize_str(r.get("grade_band")), "subject": _normalize_str(r.get("subject"))}
        if scope not in entry["scopes"]:
            entry["scopes"].append(scope)

    token_index = {(x.get("name"), x.get("role")): x for x in current_tokens}
    links: list[dict[str, Any]] = []
    updated_tokens: list[dict[str, Any]] = []

    for key, person in by_person.items():
        old = token_index.get(key)
        plain_token = old.get("plain_token") if old else None
        if not plain_token:
            plain_token = uuid.uuid4().hex + uuid.uuid4().hex
        token_record = {
            "name": person["name"],
            "role": person["role"],
            "contact": person.get("contact", ""),
            "scopes": person["scopes"],
            "token_hash": _token_hash(plain_token),
            "plain_token": plain_token,  # MVP 阶段用于可回显链接，生产请去掉
            "expires_at": payload.expires_at,
            "revoked": False,
            "updated_at": _now_iso(),
        }
        updated_tokens.append(token_record)
        links.append(
            {
                "name": person["name"],
                "role": person["role"],
                "scope": "活动全量" if person["role"] == "coordinator" else person["scopes"],
                "url": _build_front_link(activity_id, person["role"], plain_token, request),
            }
        )

    _json_dump(p["tokens"], updated_tokens)
    return {"generated": len(links), "links": links}


@router.get("/review-channel/activities/{activity_id}/access-links/export")
async def export_access_links(
    activity_id: str,
    fmt: Literal["xlsx", "csv"] = Query(default="xlsx"),
    request: Request = None,
) -> FileResponse:
    p = _ensure_activity_exists(activity_id)
    tokens = _json_load(p["tokens"], default=[])
    if not tokens:
        raise HTTPException(status_code=400, detail="暂无可导出的链接，请先生成链接")

    rows: list[dict[str, Any]] = []
    for t in tokens:
        scope_val: str
        if t.get("role") == "coordinator":
            scope_val = "活动全量"
        else:
            scopes = t.get("scopes", [])
            scope_val = "；".join(
                f"{_normalize_str(s.get('grade_band'))}-{_normalize_str(s.get('subject'))}"
                for s in scopes
                if _normalize_str(s.get("grade_band")) and _normalize_str(s.get("subject"))
            )

        token_plain = _normalize_str(t.get("plain_token"))
        rows.append(
            {
                "name": t.get("name"),
                "role": "教研员" if t.get("role") == "coordinator" else "评委",
                "contact": t.get("contact", ""),
                "scope": scope_val,
                "expires_at": t.get("expires_at", ""),
                "revoked": "是" if t.get("revoked") else "否",
                "link": _build_front_link(activity_id, _normalize_str(t.get("role")), token_plain, request) if token_plain else "",
            }
        )

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = p["exports"] / f"access-links-{ts}.{fmt}"
    columns = ["name", "role", "contact", "scope", "expires_at", "revoked", "link"]
    _write_table(file_path, rows, columns=columns, fmt=fmt)
    return FileResponse(path=file_path, filename=file_path.name)


@router.get("/review-channel/access/session")
async def get_access_session(
    token: str = Query(...),
    activity_id: Optional[str] = Query(default=None),
) -> dict[str, Any]:
    return _load_session(token=token, activity_id=activity_id)


@router.get("/review-channel/activities/{activity_id}/works")
async def list_review_works(
    activity_id: str,
    token: str = Query(...),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    grade_band: Optional[str] = Query(default=None),
    subject: Optional[str] = Query(default=None),
) -> dict[str, Any]:
    session = _load_session(token=token, activity_id=activity_id)
    works = _load_works(activity_id)
    summary = _json_load(_paths(activity_id)["summary"], default=[])
    summary_index = {x.get("work_id"): x for x in summary}

    scoped: list[dict[str, Any]] = []
    for work in works:
        # Both judges and coordinators should only see works within their assigned scopes
        if not _scope_match(work, session.get("scopes", [])):
            continue
        if grade_band and _normalize_str(work.get("grade_band")) != grade_band:
            continue
        if subject and _normalize_str(work.get("subject")) != subject:
            continue
        # Check if current judge has scored this work
        work_id = work.get("work_id")
        judge_name = session.get("name", "")
        my_score_status = "未评分"  # Default: not scored by current judge
        
        # Load score events to check if current judge has submitted
        score_events = _read_jsonl(_paths(activity_id)["scores"])
        for ev in score_events:
            if ev.get("event") == "submit" and ev.get("work_id") == work_id and ev.get("judge") == judge_name:
                my_score_status = "我已评分"
                break
        
        # Determine overall status
        overall_status = summary_index.get(work_id, {}).get("status", "未评分")
        review_count = summary_index.get(work_id, {}).get("review_count", 0)
        
        # For display: show my score status, but also indicate if others have scored
        if my_score_status == "未评分" and review_count > 0:
            display_status = "待我评分"  # Others have scored, I haven't
        else:
            display_status = my_score_status
        
        merged = {
            **work,
            "status": display_status,
            "overall_status": overall_status,  # Keep overall status for reference
            "review_count": review_count,
            "final_score": summary_index.get(work_id, {}).get("final_score"),
            "my_score_status": my_score_status,  # Explicit field for current judge
        }
        if status_filter == "scored" and merged["status"] != "已评分":
            continue
        if status_filter == "unscored" and merged["status"] != "未评分":
            continue
        scoped.append(merged)
    return {"items": scoped, "total": len(scoped)}


@router.get("/review-channel/activities/{activity_id}/works/{work_id}")
async def get_review_work_detail(
    activity_id: str,
    work_id: str,
    token: str = Query(...),
) -> dict[str, Any]:
    session = _load_session(token=token, activity_id=activity_id)
    works = _load_works(activity_id)
    work = next((w for w in works if w.get("work_id") == work_id), None)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    if not _scope_match(work, session.get("scopes", [])):
        raise HTTPException(status_code=403, detail="无权访问该作品")
    return work


@router.put("/review-channel/activities/{activity_id}/works/{work_id}/score")
async def save_score_draft(
    activity_id: str,
    work_id: str,
    payload: ScorePayload,
    token: str = Query(...),
    request_id: Optional[str] = Query(default=None),
) -> dict[str, Any]:
    session = _load_session(token=token, activity_id=activity_id)
    if session["role"] != "judge":
        raise HTTPException(status_code=403, detail="仅评委可评分")
    works = _load_works(activity_id)
    work = next((w for w in works if w.get("work_id") == work_id), None)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    if not _scope_match(work, session.get("scopes", [])):
        raise HTTPException(status_code=403, detail="无权评分该作品")

    p = _paths(activity_id)
    rid = request_id or uuid.uuid4().hex
    with _file_lock(p["lock"]):
        _append_jsonl(
            p["scores"],
            {
                "ts": _now_iso(),
                "event": "save_draft",
                "activity_id": activity_id,
                "work_id": work_id,
                "judge": session["name"],
                "score_total": payload.score_total,
                "comment": payload.comment,
                "request_id": rid,
            },
        )
    return {"ok": True}


@router.post("/review-channel/activities/{activity_id}/works/{work_id}/submit")
async def submit_score(
    activity_id: str,
    work_id: str,
    payload: ScorePayload,
    token: str = Query(...),
    request_id: Optional[str] = Query(default=None),
) -> dict[str, Any]:
    session = _load_session(token=token, activity_id=activity_id)
    if session["role"] != "judge":
        raise HTTPException(status_code=403, detail="仅评委可提交评分")
    works = _load_works(activity_id)
    work = next((w for w in works if w.get("work_id") == work_id), None)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    if not _scope_match(work, session.get("scopes", [])):
        raise HTTPException(status_code=403, detail="无权评分该作品")

    p = _paths(activity_id)
    rid = request_id or uuid.uuid4().hex
    with _file_lock(p["lock"]):
        events = _read_jsonl(p["scores"])
        if any(ev.get("request_id") == rid for ev in events):
            return {"ok": True, "idempotent": True}
        _append_jsonl(
            p["scores"],
            {
                "ts": _now_iso(),
                "event": "submit",
                "activity_id": activity_id,
                "work_id": work_id,
                "judge": session["name"],
                "score_total": payload.score_total,
                "comment": payload.comment,
                "request_id": rid,
            },
        )
    recompute = _recompute(activity_id)
    return {
        "ok": True,
        "submitted_at": _now_iso(),
        "progress": recompute["progress"],
    }


@router.get("/review-channel/activities/{activity_id}/progress")
async def get_progress(activity_id: str, token: str = Query(...)) -> dict[str, Any]:
    session = _load_session(token=token, activity_id=activity_id)
    if session["role"] != "coordinator":
        raise HTTPException(status_code=403, detail="仅教研员可查看进度")
    p = _paths(activity_id)
    
    # Get coordinator's scopes
    coordinator_scopes = session.get("scopes", [])
    
    # Load all works and filter by coordinator's scope
    all_works = _load_works(activity_id)
    scoped_works = [w for w in all_works if _scope_match(w, coordinator_scopes)]
    
    # Load summary to get scoring status
    summary = _json_load(p["summary"], default=[])
    summary_index = {x.get("work_id"): x for x in summary}
    
    # Calculate progress for scoped works only
    total_works = len(scoped_works)
    scored_works = 0
    for work in scoped_works:
        work_summary = summary_index.get(work.get("work_id"), {})
        if work_summary.get("status") == "已评分":
            scored_works += 1
    
    return {
        "total_works": total_works,
        "scored_works": scored_works,
        "unscored_works": max(total_works - scored_works, 0),
    }


@router.post("/review-channel/activities/{activity_id}/recompute")
async def recompute_summary(activity_id: str) -> dict[str, Any]:
    result = _recompute(activity_id)
    return {
        "ok": True,
        "summary_count": len(result["summary"]),
        "progress": result["progress"],
    }


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c) for c in columns})


def _write_xlsx(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([{c: row.get(c) for c in columns} for row in rows], columns=columns)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="data")


def _write_table(path: Path, rows: list[dict[str, Any]], columns: list[str], fmt: Literal["csv", "xlsx"]) -> None:
    if fmt == "csv":
        _write_csv(path, rows, columns)
        return
    _write_xlsx(path, rows, columns)


@router.get("/review-channel/activities/{activity_id}/assignment-columns")
async def get_assignment_columns(
    activity_id: str,
    max_judges_per_scope: int = Query(default=3, ge=1, le=50),
) -> dict[str, Any]:
    scopes = sorted(_extract_scopes_from_works(activity_id))

    columns: list[str] = []
    for grade_band, subject in scopes:
        prefix = f"{grade_band}{subject}"
        columns.append(f"{prefix}教研员")
        for i in range(1, max_judges_per_scope + 1):
            columns.append(f"{prefix}评委{i}")

    return {
        "activity_id": activity_id,
        "scope_count": len(scopes),
        "scopes": [{"grade_band": g, "subject": s} for g, s in scopes],
        "columns": columns,
        "example": {c: "" for c in columns},
    }


@router.get("/review-channel/activities/{activity_id}/export/details")
async def export_details(
    activity_id: str,
    token: str = Query(...),
    fmt: Literal["csv", "xlsx"] = Query(default="xlsx"),
) -> FileResponse:
    session = _load_session(token=token, activity_id=activity_id)
    if session["role"] != "coordinator":
        raise HTTPException(status_code=403, detail="仅教研员可导出")

    p = _paths(activity_id)
    works = _read_jsonl(p["works"])
    work_idx = {w.get("work_id"): w for w in works}
    events = _read_jsonl(p["scores"])
    detail_rows: list[dict[str, Any]] = []
    for ev in events:
        if ev.get("event") != "submit":
            continue
        work = work_idx.get(ev.get("work_id"), {})
        # Only include works within coordinator's scope
        if not _scope_match(work, session.get("scopes", [])):
            continue
        detail_rows.append(
            {
                "work_number": work.get("work_number"),
                "title": work.get("title"),
                "author_name": work.get("author_name", ""),
                "grade_band": work.get("grade_band"),
                "subject": work.get("subject"),
                "school_name": work.get("school_name"),
                "judge": ev.get("judge"),
                "score_total": ev.get("score_total"),
                "comment": ev.get("comment"),
                "submitted_at": ev.get("ts"),
            }
        )

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = p["exports"] / f"details-{ts}.{fmt}"
    columns = [
        "work_number",
        "title",
        "author_name",
        "grade_band",
        "subject",
        "school_name",
        "judge",
        "score_total",
        "comment",
        "submitted_at",
    ]
    _write_table(file_path, detail_rows, columns, fmt=fmt)
    return FileResponse(path=file_path, filename=file_path.name)


@router.get("/review-channel/activities/{activity_id}/export/summary")
async def export_summary(
    activity_id: str,
    token: str = Query(...),
    fmt: Literal["csv", "xlsx"] = Query(default="xlsx"),
) -> FileResponse:
    session = _load_session(token=token, activity_id=activity_id)
    if session["role"] != "coordinator":
        raise HTTPException(status_code=403, detail="仅教研员可导出")

    p = _paths(activity_id)
    
    # Load works and score events
    works = _read_jsonl(p["works"])
    work_idx = {w.get("work_id"): w for w in works}
    events = _read_jsonl(p["scores"])
    
    # Filter works by coordinator's scope
    coordinator_scopes = session.get("scopes", [])
    scoped_work_ids = set()
    for work in works:
        if _scope_match(work, coordinator_scopes):
            scoped_work_ids.add(work.get("work_id"))
    
    # Organize scores by work and judge (keep only the last submit from each judge)
    work_judge_scores: dict[str, dict[str, dict[str, Any]]] = {}
    all_judges: set[str] = set()
    
    for ev in events:
        if ev.get("event") != "submit":
            continue
        work_id = ev.get("work_id")
        if work_id not in scoped_work_ids:
            continue
        judge = ev.get("judge", "")
        all_judges.add(judge)
        
        if work_id not in work_judge_scores:
            work_judge_scores[work_id] = {}
        # Keep only the last submit from each judge
        work_judge_scores[work_id][judge] = {
            "score_total": ev.get("score_total"),
            "comment": ev.get("comment", ""),
            "submitted_at": ev.get("ts"),
        }
    
    # Sort judges alphabetically for consistent column order
    sorted_judges = sorted(all_judges)
    
    # Build summary rows with individual judge scores
    summary_rows: list[dict[str, Any]] = []
    for work in works:
        work_id = work.get("work_id")
        if work_id not in scoped_work_ids:
            continue
        
        row: dict[str, Any] = {
            "work_number": work.get("work_number"),
            "title": work.get("title"),
            "author_name": work.get("author_name", ""),
            "grade_band": work.get("grade_band"),
            "subject": work.get("subject"),
            "school_name": work.get("school_name"),
        }
        
        # Add columns for each judge
        judge_scores = []
        for judge in sorted_judges:
            score_data = work_judge_scores.get(work_id, {}).get(judge)
            if score_data:
                row[f"{judge}_分数"] = score_data["score_total"]
                row[f"{judge}_评语"] = score_data["comment"]
                judge_scores.append(score_data["score_total"])
            else:
                row[f"{judge}_分数"] = ""
                row[f"{judge}_评语"] = ""
        
        # Calculate average score
        if judge_scores:
            row["平均分"] = round(sum(judge_scores) / len(judge_scores), 1)
            row["评分人数"] = len(judge_scores)
            row["状态"] = "已评分" if len(judge_scores) > 0 else "未评分"
        else:
            row["平均分"] = ""
            row["评分人数"] = 0
            row["状态"] = "未评分"
        
        summary_rows.append(row)
    
    # Build columns: base columns + judge columns (分数 and 评语 for each judge)
    columns = [
        "work_number",
        "title",
        "author_name",
        "grade_band",
        "subject",
        "school_name",
    ]
    for judge in sorted_judges:
        columns.extend([f"{judge}_分数", f"{judge}_评语"])
    columns.extend(["平均分", "评分人数", "状态"])
    
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = p["exports"] / f"summary-{ts}.{fmt}"
    _write_table(file_path, summary_rows, columns, fmt=fmt)
    return FileResponse(path=file_path, filename=file_path.name)
