"""
学生个人知识库 — 先前知识查询（移植 wiki-query，自然语言摘要）
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.knowledge_base import knowledge_base_service

logger = logging.getLogger(__name__)


class KnowledgeQueryService:
    """根据问题检索学生 vault，返回自然语言先前知识摘要。"""

    async def query_prior_knowledge(
        self,
        db: AsyncSession,
        student_id: int,
        question_text: str,
        *,
        mode: str = "standard",
    ) -> str:
        _ = db  # reserved for future LLM channel via ai_settings
        _ = mode
        if not question_text or not question_text.strip():
            return ""
        if not knowledge_base_service.vault_exists(student_id):
            return ""

        hot = knowledge_base_service.read_text(student_id, "wiki/hot.md")
        index = knowledge_base_service.read_text(student_id, "wiki/index.md")
        tokens = self._tokenize(question_text)

        # Quick path: hot.md already relevant
        if hot and self._score_text(hot, tokens) > 0:
            excerpt = self._excerpt(hot, 280)
            if excerpt and "暂无近期" not in excerpt:
                return (
                    "根据你的知识库近期记录："
                    f"{excerpt}"
                    " 本次可先对照这些已有理解再检查新题。"
                )

        candidates = self._pick_pages(student_id, index, tokens, limit=5)
        if not candidates:
            # Fall back to scanning question notes by filename/content keywords
            listed = knowledge_base_service.list_notes(student_id)
            scored: List[Tuple[float, str, str]] = []
            for item in listed.get("items") or []:
                path = item["path"]
                if not path.startswith("wiki/questions/") and not path.startswith("wiki/concepts/"):
                    continue
                text = knowledge_base_service.read_text(student_id, path)
                score = self._score_text(f"{item.get('title', '')}\n{text}", tokens)
                if score > 0:
                    scored.append((score, path, text))
            scored.sort(key=lambda x: x[0], reverse=True)
            candidates = [(p, t) for _, p, t in scored[:5]]

        if not candidates:
            return ""

        bullets: List[str] = []
        for path, text in candidates[:3]:
            title = knowledge_base_service._extract_title_from_text(
                text, path.rsplit("/", 1)[-1]
            )
            snippet = self._pick_relevant_snippet(text, tokens) or self._excerpt(text, 80)
            bullets.append(f"你在「{title}」中已有记录：{snippet}")

        joined = "；".join(bullets)
        return f"根据你的知识库：{joined}。本次答疑可先确认是否又卡在相似点上。"

    def _pick_pages(
        self,
        student_id: int,
        index_text: str,
        tokens: List[str],
        *,
        limit: int,
    ) -> List[Tuple[str, str]]:
        if not index_text:
            return []
        # Parse lines like: - [[Title]] (`wiki/questions/....md`) — desc
        pattern = re.compile(r"\(`([^`]+)`\)")
        paths: List[str] = []
        for line in index_text.splitlines():
            m = pattern.search(line)
            if not m:
                continue
            path = m.group(1).strip()
            if self._score_text(line, tokens) > 0:
                paths.append(path)

        results: List[Tuple[str, str]] = []
        for path in paths[:limit]:
            text = knowledge_base_service.read_text(student_id, path)
            if text:
                results.append((path, text))
        return results

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        # Keep CJK bigrams + ascii words
        text = text.strip().lower()
        tokens: List[str] = []
        for m in re.finditer(r"[a-z0-9_]{2,}|[\u4e00-\u9fff]{1,}", text):
            tok = m.group(0)
            if len(tok) == 1 and "\u4e00" <= tok <= "\u9fff":
                continue
            tokens.append(tok)
        # Also add 2-char CJK windows from continuous runs
        for run in re.findall(r"[\u4e00-\u9fff]{2,}", text):
            for i in range(len(run) - 1):
                tokens.append(run[i : i + 2])
        # Dedupe preserving order
        seen = set()
        out: List[str] = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out[:40]

    @staticmethod
    def _score_text(text: str, tokens: List[str]) -> float:
        if not text or not tokens:
            return 0.0
        lower = text.lower()
        score = 0.0
        for tok in tokens:
            if tok in lower:
                score += 1.0 if len(tok) > 1 else 0.3
        return score

    @staticmethod
    def _excerpt(text: str, max_len: int) -> str:
        body = text
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                body = text[end + 4 :]
        # Drop headings-only noise
        lines = [
            ln.strip()
            for ln in body.splitlines()
            if ln.strip() and not ln.strip().startswith("#") and not ln.strip().startswith("---")
        ]
        joined = " ".join(lines)
        joined = re.sub(r"\s+", " ", joined).strip()
        if len(joined) > max_len:
            return joined[:max_len].rstrip() + "…"
        return joined

    def _pick_relevant_snippet(self, text: str, tokens: List[str]) -> str:
        body = text
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                body = text[end + 4 :]
        best = ""
        best_score = 0.0
        for para in re.split(r"\n\s*\n", body):
            cleaned = re.sub(r"\s+", " ", para).strip()
            if len(cleaned) < 8 or cleaned.startswith("#"):
                continue
            score = self._score_text(cleaned, tokens)
            if score > best_score:
                best_score = score
                best = cleaned
        if not best:
            return ""
        if len(best) > 100:
            return best[:100].rstrip() + "…"
        return best


knowledge_query_service = KnowledgeQueryService()
