"""
MathLab 课程手册检索 — 供自主学习微课 grounding
读取 frontend/public/mathlab/data/manuals/*.json
"""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)


def _default_manuals_root() -> str:
    configured = getattr(settings, "MATHLAB_MANUALS_ROOT", None)
    if configured:
        return os.path.realpath(configured)
    # backend/ -> repo root -> frontend/public/mathlab/data/manuals
    here = os.path.dirname(os.path.abspath(__file__))
    backend_root = os.path.abspath(os.path.join(here, "..", ".."))
    candidate = os.path.join(
        backend_root,
        "..",
        "frontend",
        "public",
        "mathlab",
        "data",
        "manuals",
    )
    return os.path.realpath(candidate)


class MathLabCurriculumIndex:
    def __init__(self, manuals_root: Optional[str] = None):
        self.manuals_root = manuals_root or _default_manuals_root()
        self._tasks: List[Dict[str, Any]] = []
        self._loaded = False

    def reload(self) -> None:
        self._tasks = []
        self._loaded = False
        self._ensure_loaded()

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        index_path = os.path.join(self.manuals_root, "index.json")
        if not os.path.isfile(index_path):
            logger.warning("MathLab manuals index not found: %s", index_path)
            return
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                index = json.load(f)
        except Exception:
            logger.exception("failed to read MathLab manuals index")
            return

        volumes = []
        volumes.extend(index.get("stageVolumes") or [])
        volumes.extend(index.get("subjectVolumes") or [])
        for vol in volumes:
            rel = str(vol.get("path") or "").lstrip("./")
            if not rel:
                continue
            path = os.path.join(self.manuals_root, rel)
            self._load_volume(path, vol)

    def _load_volume(self, path: str, vol_meta: Dict[str, Any]) -> None:
        if not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            logger.exception("failed to read MathLab volume %s", path)
            return

        stage_name = data.get("stageName") or vol_meta.get("stageName") or ""
        for section in data.get("sections") or []:
            grade_name = section.get("gradeName") or section.get("title") or ""
            for task in section.get("tasks") or []:
                if not isinstance(task, dict):
                    continue
                task_id = str(task.get("id") or "").strip()
                if not task_id:
                    continue
                self._tasks.append(
                    {
                        "id": task_id,
                        "title": str(task.get("title") or ""),
                        "unit": str(task.get("unit") or ""),
                        "stage_name": stage_name,
                        "grade_name": grade_name,
                        "scene": str(task.get("scene") or ""),
                        "tags": [str(t) for t in (task.get("tags") or []) if str(t).strip()],
                        "goals": [str(g) for g in (task.get("goals") or []) if str(g).strip()],
                        "challenges": [
                            str(c) for c in (task.get("challenges") or []) if str(c).strip()
                        ],
                        "hint": str(task.get("hint") or ""),
                        "focus": str(task.get("focus") or ""),
                        "formulas": task.get("formulas") or [],
                        "mathlab_url": f"/mathlab/index.html?task={task_id}",
                    }
                )

    def search(self, query: str, *, limit: int = 3) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        tokens = self._tokenize(query)
        if not tokens or not self._tasks:
            return []

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for task in self._tasks:
            hay = " ".join(
                [
                    task["id"],
                    task["title"],
                    task["unit"],
                    task["stage_name"],
                    task["grade_name"],
                    task["scene"],
                    task["hint"],
                    task["focus"],
                    " ".join(task["tags"]),
                    " ".join(task["goals"]),
                    " ".join(task["challenges"]),
                ]
            ).lower()
            score = 0.0
            for tok in tokens:
                if tok in hay:
                    # Prefer title/unit/tag hits
                    if tok in (task["title"] + task["unit"]).lower():
                        score += 3.0
                    elif tok in " ".join(task["tags"]).lower():
                        score += 2.5
                    elif tok in task["scene"].lower():
                        score += 2.0
                    else:
                        score += 1.0
            # Boost explicit robot/mathlab-ish queries when scene matches circle/shape/path
            if any(k in query for k in ("圆", "圆周", "画圆", "巡检")) and task["scene"] == "circle":
                score += 4.0
            if any(k in query for k in ("走图形", "多边形", "三角形", "平行四边形")) and task[
                "scene"
            ] == "shape":
                score += 3.0
            if any(k in query for k in ("轮式", "机器人", "mathlab", "仿真", "积木")):
                score += 0.5
            if score > 0:
                scored.append((score, task))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [dict(t) for _, t in scored[:limit]]

    def format_context_for_prompt(self, matches: List[Dict[str, Any]]) -> str:
        if not matches:
            return ""
        blocks: List[str] = []
        for i, task in enumerate(matches, start=1):
            formulas = []
            for f in task.get("formulas") or []:
                if isinstance(f, dict):
                    formulas.append(f"{f.get('title') or ''}: {f.get('tex') or ''}".strip())
            blocks.append(
                "\n".join(
                    [
                        f"[{i}] MathLab课例 {task['id']} · {task['title']}",
                        f"学段/单元：{task.get('stage_name') or ''} / {task.get('unit') or ''}",
                        f"场景：{task.get('scene') or ''}",
                        f"标签：{'、'.join(task.get('tags') or []) or '无'}",
                        f"目标：{'；'.join(task.get('goals') or []) or '无'}",
                        f"挑战：{'；'.join(task.get('challenges') or []) or '无'}",
                        f"提示：{task.get('hint') or '无'}",
                        f"公式：{'；'.join(formulas) or '无'}",
                        f"实操链接：{task.get('mathlab_url')}",
                    ]
                )
            )
        return "\n\n".join(blocks)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        text = (text or "").strip().lower()
        tokens: List[str] = []
        for m in re.finditer(r"[a-z0-9_]{2,}|[\u4e00-\u9fff]{1,}", text):
            tok = m.group(0)
            if len(tok) == 1 and "\u4e00" <= tok <= "\u9fff":
                continue
            tokens.append(tok)
        for run in re.findall(r"[\u4e00-\u9fff]{2,}", text):
            for i in range(len(run) - 1):
                tokens.append(run[i : i + 2])
        # Keep useful singles for MathLab
        for special in ("圆", "弧", "π", "比"):
            if special in text:
                tokens.append(special)
        seen = set()
        out: List[str] = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out[:50]


@lru_cache(maxsize=1)
def get_mathlab_curriculum_index() -> MathLabCurriculumIndex:
    return MathLabCurriculumIndex()


mathlab_curriculum_index = get_mathlab_curriculum_index()
