"""
学生个人知识库 — 答疑会话入库（移植 wiki-ingest 工作流）
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.knowledge_base import knowledge_base_service

logger = logging.getLogger(__name__)


class KnowledgeIngestService:
    """把答疑会话摘要写入学生 vault。"""

    def ingest_from_self_study_session(
        self,
        student_id: int,
        *,
        session_id: int,
        summary_before: str,
        summary_after: str,
        problem_text: Optional[str] = None,
        student_work_text: Optional[str] = None,
        result_judgment: Optional[str] = None,
        primary_error_type: Optional[str] = None,
        ai_guidance_summary: Optional[List[str]] = None,
    ) -> str:
        knowledge_base_service.ensure_vault(student_id)
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rel_path = f"wiki/questions/{day}-session-{session_id}.md"
        concepts = self._extract_concepts(
            summary_before=summary_before,
            summary_after=summary_after,
            problem_text=problem_text,
            primary_error_type=primary_error_type,
        )
        title = f"答疑会话 #{session_id}"
        body = self._build_question_page(
            title=title,
            session_id=session_id,
            summary_before=summary_before,
            summary_after=summary_after,
            problem_text=problem_text,
            student_work_text=student_work_text,
            result_judgment=result_judgment,
            primary_error_type=primary_error_type,
            ai_guidance_summary=ai_guidance_summary or [],
            concepts=concepts,
        )
        knowledge_base_service.write_note(student_id, rel_path, body)

        for concept in concepts:
            self._upsert_concept(student_id, concept, session_id, rel_path, summary_after)

        desc = (summary_after or summary_before or "答疑沉淀").strip().replace("\n", " ")
        if len(desc) > 60:
            desc = desc[:60] + "…"
        knowledge_base_service.upsert_index_entry(student_id, title, rel_path, desc)

        hot_block = (
            f"### {day} · 会话 #{session_id}\n"
            f"- 原来：{(summary_before or '').strip()[:80]}\n"
            f"- 现在：{(summary_after or '').strip()[:80]}\n"
        )
        if concepts:
            links = "、".join(f"[[{c}]]" for c in concepts)
            hot_block += f"- 相关：{links}\n"
        knowledge_base_service.update_hot(student_id, hot_block)
        knowledge_base_service.append_log(
            student_id,
            f"ingest self-study session #{session_id} → {rel_path}",
        )
        return rel_path

    def _extract_concepts(
        self,
        *,
        summary_before: str,
        summary_after: str,
        problem_text: Optional[str],
        primary_error_type: Optional[str],
    ) -> List[str]:
        text = " ".join(
            filter(
                None,
                [
                    summary_before,
                    summary_after,
                    problem_text or "",
                ],
            )
        )
        concepts: List[str] = []
        # Lightweight keyword heuristics for primary-school math themes
        keyword_map = [
            ("通分", "分数通分"),
            ("约分", "分数约分"),
            ("分数", "分数运算"),
            ("小数", "小数运算"),
            ("面积", "面积计算"),
            ("周长", "周长计算"),
            ("体积", "体积计算"),
            ("单位", "单位换算"),
            ("竖式", "竖式计算"),
            ("进位", "进位加法"),
            ("退位", "退位减法"),
            ("乘法", "乘法运算"),
            ("除法", "除法运算"),
            ("方程", "简易方程"),
            ("比例", "比例关系"),
            ("百分", "百分数"),
        ]
        for needle, label in keyword_map:
            if needle in text and label not in concepts:
                concepts.append(label)
            if len(concepts) >= 3:
                break

        error_map = {
            "reading_error": "审题理解",
            "relation_error": "数量关系",
            "calculation_error": "计算过程",
            "unit_expression_error": "单位与表达",
            "explanation_gap": "说理表达",
        }
        if primary_error_type:
            key = getattr(primary_error_type, "value", primary_error_type)
            label = error_map.get(str(key))
            if label and label not in concepts:
                concepts.append(label)

        return concepts[:3]

    def _build_question_page(
        self,
        *,
        title: str,
        session_id: int,
        summary_before: str,
        summary_after: str,
        problem_text: Optional[str],
        student_work_text: Optional[str],
        result_judgment: Optional[str],
        primary_error_type: Optional[str],
        ai_guidance_summary: List[str],
        concepts: List[str],
    ) -> str:
        related = ", ".join(f'"{c}"' for c in concepts) if concepts else ""
        judgment = getattr(result_judgment, "value", result_judgment) or ""
        error_type = getattr(primary_error_type, "value", primary_error_type) or ""
        concept_links = "、".join(f"[[{c}]]" for c in concepts) if concepts else "（暂无）"
        guidance = "\n".join(f"- {line}" for line in ai_guidance_summary[:6]) or "- （无）"

        return f"""---
type: question
session_id: {session_id}
status: evergreen
result_judgment: "{judgment}"
primary_error_type: "{error_type}"
related: [{related}]
---

# {title}

## 我原来为什么错

{(summary_before or "").strip() or "（未填写）"}

## 我现在为什么知道这样改对了

{(summary_after or "").strip() or "（未填写）"}

## 题目与作答预览

- 题干：{(problem_text or "暂无").strip()[:300]}
- 作答：{(student_work_text or "暂无").strip()[:300]}

## AI 引导要点

{guidance}

## 相关概念

{concept_links}
"""

    def _upsert_concept(
        self,
        student_id: int,
        concept: str,
        session_id: int,
        question_path: str,
        summary_after: str,
    ) -> None:
        safe_name = re.sub(r'[\\/:*?"<>|]', "_", concept).strip() or "未命名概念"
        rel_path = f"wiki/concepts/{safe_name}.md"
        existing = knowledge_base_service.read_text(student_id, rel_path)
        link_line = f"- 来自答疑会话 #{session_id}：[[答疑会话 #{session_id}]]（`{question_path}`）"
        snippet = (summary_after or "").strip().replace("\n", " ")
        if len(snippet) > 100:
            snippet = snippet[:100] + "…"

        if not existing:
            content = f"""---
type: concept
status: seedling
tags: []
---

# {concept}

## 我的理解

{snippet or "（待补充）"}

## 相关答疑

{link_line}
"""
            knowledge_base_service.write_note(student_id, rel_path, content)
            knowledge_base_service.upsert_index_entry(
                student_id,
                concept,
                rel_path,
                snippet or "概念笔记",
            )
            return

        if f"session-{session_id}" in existing or f"会话 #{session_id}" in existing:
            return
        knowledge_base_service.append_note(student_id, rel_path, f"\n{link_line}\n")

    def ingest_from_self_directed_session(
        self,
        student_id: int,
        *,
        session_id: int,
        goal_text: str,
        mission_why: Optional[str],
        lesson: Dict[str, Any],
        mastery_answer: str,
        prior_summary: Optional[str] = None,
    ) -> str:
        knowledge_base_service.ensure_vault(student_id)
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        title = str(lesson.get("title") or f"自主学习 #{session_id}").strip()
        slug = self._slugify(title) or f"session-{session_id}"
        lesson_path = f"wiki/lessons/{day}-{slug}.md"
        concepts = [
            str(tag).strip()
            for tag in (lesson.get("concept_tags") or [])
            if str(tag).strip()
        ][:5]
        if not concepts:
            concepts = self._extract_concepts(
                summary_before=goal_text,
                summary_after=mastery_answer,
                problem_text=str(lesson.get("objective") or ""),
                primary_error_type=None,
            )

        concept_links = "、".join(f"[[{c}]]" for c in concepts) if concepts else "（暂无）"
        lesson_body = f"""---
type: lesson
session_id: {session_id}
status: evergreen
source: self_directed
related: [{", ".join(f'"{c}"' for c in concepts)}]
---

# {title}

## 学习目标

{(lesson.get("objective") or goal_text).strip()}

## 为什么学

{(mission_why or "未填写").strip()}

## 讲解摘要

{(lesson.get("explanation_md") or "").strip() or "（无）"}

## 我的验收回答

{mastery_answer.strip() or "（未填写）"}

## 相关概念

{concept_links}
"""
        knowledge_base_service.write_note(student_id, lesson_path, lesson_body)

        record_no = self._next_learning_record_number(student_id)
        record_slug = self._slugify(title) or "lesson"
        record_path = f"wiki/learning-records/{record_no:04d}-{record_slug}.md"
        record_body = f"""---
type: learning_record
session_id: {session_id}
status: active
---

# 学会了：{title}

学生围绕「{goal_text.strip()}」完成一节微课，并能用自己的话说明：{(mastery_answer or "").strip()[:120]}。
这对后续答疑与再学习有帮助：可从已掌握的关键步骤继续，而不是从头重复。

相关课程：[[{title}]]（`{lesson_path}`）
"""
        knowledge_base_service.write_note(student_id, record_path, record_body)

        reference_md = str(lesson.get("reference_card_md") or "").strip()
        if reference_md:
            ref_name = concepts[0] if concepts else title
            safe = re.sub(r'[\\/:*?"<>|]', "_", ref_name).strip() or "参考卡"
            ref_path = f"wiki/reference/{safe}.md"
            if not knowledge_base_service.read_text(student_id, ref_path):
                knowledge_base_service.write_note(
                    student_id,
                    ref_path,
                    f"---\ntype: reference\n---\n\n{reference_md}\n",
                )
                knowledge_base_service.upsert_index_entry(
                    student_id,
                    f"参考卡·{ref_name}",
                    ref_path,
                    "自主学习参考卡",
                )

        for concept in concepts:
            self._upsert_concept(
                student_id,
                concept,
                session_id,
                lesson_path,
                mastery_answer,
            )

        desc = (mastery_answer or goal_text).strip().replace("\n", " ")
        if len(desc) > 60:
            desc = desc[:60] + "…"
        knowledge_base_service.upsert_index_entry(student_id, title, lesson_path, desc)
        knowledge_base_service.upsert_index_entry(
            student_id,
            f"学习记录·{title}",
            record_path,
            "自主学习沉淀",
        )

        hot_block = (
            f"### {day} · 自主学习 #{session_id}\n"
            f"- 目标：{goal_text.strip()[:80]}\n"
            f"- 验收：{(mastery_answer or '').strip()[:80]}\n"
        )
        if concepts:
            hot_block += f"- 相关：{'、'.join(f'[[{c}]]' for c in concepts)}\n"
        if prior_summary:
            hot_block += f"- 开课先前知识已参考\n"
        knowledge_base_service.update_hot(student_id, hot_block)
        knowledge_base_service.append_log(
            student_id,
            f"ingest self-directed session #{session_id} → {lesson_path}",
        )
        return lesson_path

    def _next_learning_record_number(self, student_id: int) -> int:
        listed = knowledge_base_service.list_notes(student_id)
        max_n = 0
        for item in listed.get("items") or []:
            path = item.get("path") or ""
            if not path.startswith("wiki/learning-records/"):
                continue
            name = path.rsplit("/", 1)[-1]
            m = re.match(r"^(\d+)-", name)
            if m:
                max_n = max(max_n, int(m.group(1)))
        return max_n + 1

    @staticmethod
    def _slugify(text: str) -> str:
        text = re.sub(r"\s+", "-", (text or "").strip())
        text = re.sub(r"[^\w\u4e00-\u9fff\-]+", "", text)
        return text[:40].strip("-")


knowledge_ingest_service = KnowledgeIngestService()
