"""
自主学习微课生成与练习反馈（移植 /teach 一课结构）
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.ai_settings import AIChannelRuntimeConfig, ai_settings_service
from app.services.mathlab_curriculum import mathlab_curriculum_index

logger = logging.getLogger(__name__)


class SelfDirectedLessonService:
    def _has_ai(self) -> bool:
        return bool(getattr(settings, "OPENAI_API_KEY", ""))

    async def generate_lesson(
        self,
        db: AsyncSession,
        *,
        goal_text: str,
        mission_why: Optional[str],
        mission_success: Optional[str],
        prior_summary: str,
        tutor_style: str = "default",
    ) -> Dict[str, Any]:
        runtime = await ai_settings_service.get_runtime_config(db)
        text_config = runtime.text
        curriculum_matches = mathlab_curriculum_index.search(goal_text, limit=3)
        curriculum_context = mathlab_curriculum_index.format_context_for_prompt(curriculum_matches)
        prompt = self._build_generate_prompt(
            goal_text=goal_text,
            mission_why=mission_why,
            mission_success=mission_success,
            prior_summary=prior_summary,
            tutor_style=tutor_style,
            curriculum_context=curriculum_context,
        )
        fallback = self._mock_lesson(goal_text, mission_success, curriculum_matches)
        result = await self._call_text_json(prompt=prompt, channel_config=text_config, fallback=fallback)
        lesson = self._normalize_lesson(result or fallback, goal_text)
        lesson["curriculum_sources"] = [
            {
                "id": m["id"],
                "title": m["title"],
                "unit": m.get("unit") or "",
                "stage_name": m.get("stage_name") or "",
                "mathlab_url": m.get("mathlab_url") or f"/mathlab/index.html?task={m['id']}",
                "goals": (m.get("goals") or [])[:3],
                "hint": m.get("hint") or "",
            }
            for m in curriculum_matches
        ]
        return lesson

    async def grade_practice(
        self,
        db: AsyncSession,
        *,
        lesson: Dict[str, Any],
        answers: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        practice = lesson.get("practice") or []
        by_id = {str(item.get("id")): item for item in practice if isinstance(item, dict)}
        runtime = await ai_settings_service.get_runtime_config(db)
        text_config = runtime.text

        items: List[Dict[str, Any]] = []
        for ans in answers:
            pid = str(ans.get("id") or "")
            answer_text = str(ans.get("answer") or "").strip()
            item = by_id.get(pid) or {}
            qtype = str(item.get("type") or "short_answer").strip().lower()

            if qtype == "multiple_choice":
                graded = self._grade_multiple_choice(item, answer_text)
                items.append({"id": pid, **graded})
                continue

            prompt = (
                "你是小学数学助教。根据题目与评分要点，判断学生简答是否基本正确。"
                "只返回 JSON：{\"ok\":true|false,\"feedback\":\"给学生看的一句中文反馈\"}。"
                f"题目：{item.get('prompt') or ''}。"
                f"评分要点：{item.get('rubric') or ''}。"
                f"学生回答：{answer_text}。"
            )
            fallback = {
                "ok": bool(answer_text) and any(
                    tok in answer_text for tok in re.findall(r"[\u4e00-\u9fff]{2,}", str(item.get("rubric") or ""))
                ),
                "feedback": "先对照题目要求，用自己的话再讲清楚关键一步。",
            }
            if fallback["ok"]:
                fallback["feedback"] = "说得不错，关键点已经提到了。"
            graded = await self._call_text_json(prompt=prompt, channel_config=text_config, fallback=fallback)
            items.append(
                {
                    "id": pid,
                    "ok": bool((graded or fallback).get("ok")),
                    "feedback": str((graded or fallback).get("feedback") or fallback["feedback"]),
                }
            )
        return items

    def _grade_multiple_choice(self, item: Dict[str, Any], answer_text: str) -> Dict[str, Any]:
        correct = str(item.get("correct_option") or "").strip().upper()
        chosen = answer_text.strip().upper()
        options = item.get("options") if isinstance(item.get("options"), list) else []
        label_map = {}
        for opt in options:
            if not isinstance(opt, dict):
                continue
            key = str(opt.get("key") or "").strip().upper()
            label_map[key] = str(opt.get("label") or "").strip()

        if not chosen:
            return {"ok": False, "feedback": "请先选择一个选项。"}
        if correct and chosen == correct:
            return {"ok": True, "feedback": f"选对了：{chosen}。{label_map.get(correct, '')}".strip()}
        correct_text = label_map.get(correct, "")
        hint = f"正确答案是 {correct}" + (f"：{correct_text}" if correct_text else "") + "。"
        return {"ok": False, "feedback": f"这题还不太对。{hint}再对照讲解想一想。"}

    def _build_generate_prompt(
        self,
        *,
        goal_text: str,
        mission_why: Optional[str],
        mission_success: Optional[str],
        prior_summary: str,
        tutor_style: str,
        curriculum_context: str = "",
    ) -> str:
        curriculum_rule = (
            "若下方提供了「平台 MathLab 课程手册」匹配课例，必须以此为 grounding："
            "讲解要引用具体课例标题/目标/挑战/公式/提示，告诉学生在仿真里怎么做；"
            "练习题尽量围绕该课例的具体操作或公式，禁止只给空泛学习方法。"
            "在 explanation_md 末尾用一小段写「去 MathLab 实操」并写出课例 id 与链接。"
            if curriculum_context
            else "当前未匹配到 MathLab 课例时，再按通用方法教，但仍要具体可操作。"
        )
        return (
            "你是小学数学个性化学习教练，要生成「一节微课」。"
            "要求：只教一个紧窄主题；讲解短、适合小学生；"
            "练习必须包含：2 道四选一选择题（type=multiple_choice）+ 1 道简答题（type=short_answer）；"
            "另有一句验收提问；若先前知识显示学生已会一部分，从易错点或进阶一小步切入，不要从头复读。"
            f"{curriculum_rule}"
            "只返回 JSON，字段："
            "{"
            "\"title\":string,"
            "\"objective\":string,"
            "\"explanation_md\":string,"
            "\"diagram_mermaid\":string|null,"
            "\"practice\":["
            "{\"id\":string,\"prompt\":string,\"type\":\"multiple_choice\","
            "\"options\":[{\"key\":\"A\",\"label\":string},{\"key\":\"B\",\"label\":string},"
            "{\"key\":\"C\",\"label\":string},{\"key\":\"D\",\"label\":string}],"
            "\"correct_option\":\"A|B|C|D\",\"rubric\":string},"
            "{\"id\":string,\"prompt\":string,\"type\":\"short_answer\",\"rubric\":string}"
            "],"
            "\"mastery_prompt\":string,"
            "\"reference_card_md\":string,"
            "\"concept_tags\":[string]"
            "}。"
            f"助教风格：{tutor_style}。"
            f"学生目标：{goal_text}。"
            f"为什么学：{mission_why or '未填写'}。"
            f"成功标准：{mission_success or '能用自己的话讲清楚并做对一道简单题'}。"
            f"先前知识：{prior_summary or '暂无'}。"
            f"平台 MathLab 课程手册匹配：\n{curriculum_context or '无匹配课例'}。"
        )

    def _mock_lesson(
        self,
        goal_text: str,
        mission_success: Optional[str],
        curriculum_matches: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        topic = (goal_text or "这个知识点").strip()[:40]
        matches = curriculum_matches or []
        if matches:
            top = matches[0]
            goals = "；".join((top.get("goals") or [])[:3]) or "完成仿真挑战"
            challenges = "；".join((top.get("challenges") or [])[:3]) or "按提示完成路径"
            hint = top.get("hint") or "先调好左右轮速度差，再观察轨迹"
            url = top.get("mathlab_url") or f"/mathlab/index.html?task={top['id']}"
            task_id = str(top.get("id") or "")
            return {
                "title": f"微课：{top.get('title') or topic}",
                "objective": mission_success
                or f"结合 MathLab「{top.get('title')}」，能说出关键操作并完成一个挑战。",
                "explanation_md": (
                    f"## 今天跟平台课例学\n\n"
                    f"你的目标「{topic}」对应 MathLab 课例 **{task_id} · {top.get('title')}**"
                    f"（{top.get('stage_name') or ''} / {top.get('unit') or ''}）。\n\n"
                    f"**课例目标**：{goals}\n\n"
                    f"**建议挑战**：{challenges}\n\n"
                    f"**操作提示**：{hint}\n\n"
                    f"先弄清：圆/路径要靠什么参数控制？再打开仿真动手试。\n\n"
                    f"### 去 MathLab 实操\n\n"
                    f"打开 [{top.get('title')}]({url})，按挑战逐步完成。"
                ),
                "diagram_mermaid": (
                    "flowchart TD\n"
                    f'  A["目标：{topic}"] --> B["课例 {task_id}"]\n'
                    '  B --> C["看目标与公式"]\n'
                    '  C --> D["仿真走圆形/路径"]'
                ),
                "practice": [
                    {
                        "id": "p1",
                        "prompt": f"在课例「{top.get('title')}」里，第一步最该做什么？",
                        "type": "multiple_choice",
                        "options": [
                            {"key": "A", "label": "先读课例目标与挑战，再进仿真"},
                            {"key": "B", "label": "不管说明直接乱调参数"},
                            {"key": "C", "label": "只背公式不进仿真"},
                            {"key": "D", "label": "跳过挑战看下一课"},
                        ],
                        "correct_option": "A",
                        "rubric": "选 A",
                    },
                    {
                        "id": "p2",
                        "prompt": "轮式机器人要走出接近圆形的轨迹，更关键的是？",
                        "type": "multiple_choice",
                        "options": [
                            {"key": "A", "label": "左右轮保持合适的速度差并稳定前进"},
                            {"key": "B", "label": "只把一边轮子完全停下"},
                            {"key": "C", "label": "只改颜色不改速度"},
                            {"key": "D", "label": "随便点几下按钮即可"},
                        ],
                        "correct_option": "A",
                        "rubric": "选 A",
                    },
                    {
                        "id": "p3",
                        "prompt": f"打开课例 {top.get('id')} 后，你打算先完成哪一个挑战？为什么？",
                        "type": "short_answer",
                        "rubric": "提到具体挑战，并说明与目标的关系",
                    },
                ],
                "mastery_prompt": f"用自己的话讲：课例 {top.get('id')} 里怎样让机器人走出圆形？",
                "reference_card_md": (
                    f"## {top.get('title')}\n\n"
                    f"- 课例：`{top.get('id')}`\n"
                    f"- 目标：{goals}\n"
                    f"- 提示：{hint}\n"
                    f"- 实操：{url}\n"
                ),
                "concept_tags": [top.get("unit") or topic, top.get("id"), "MathLab"],
            }

        return {
            "title": f"微课：{topic}",
            "objective": mission_success
            or f"能说出「{topic}」的关键一步，并用自己的话讲清楚。",
            "explanation_md": (
                f"## 今天只学一件事\n\n"
                f"围绕「{topic}」，先弄清它在问什么，再记住最关键的一步。"
                f"先别急着做很多题，先能讲明白。\n\n"
                f"1. 题目在问什么？\n"
                f"2. 关键一步是什么？\n"
                f"3. 用自己的话复述一遍。"
            ),
            "diagram_mermaid": (
                'flowchart TD\n'
                f'  A["目标：{topic}"] --> B["关键一步"]\n'
                '  B --> C["用自己的话讲出来"]'
            ),
            "practice": [
                {
                    "id": "p1",
                    "prompt": f"学习「{topic}」时，第一步最应该做什么？",
                    "type": "multiple_choice",
                    "options": [
                        {"key": "A", "label": "先看清题目在问什么"},
                        {"key": "B", "label": "先把答案写出来"},
                        {"key": "C", "label": "先跳过讲解直接做很多题"},
                        {"key": "D", "label": "先背公式不管题意"},
                    ],
                    "correct_option": "A",
                    "rubric": "选 A",
                },
                {
                    "id": "p2",
                    "prompt": f"怎样才算真正学会了「{topic}」？",
                    "type": "multiple_choice",
                    "options": [
                        {"key": "A", "label": "只看过一遍讲解"},
                        {"key": "B", "label": "能用自己的话讲出关键一步"},
                        {"key": "C", "label": "把答案抄下来"},
                        {"key": "D", "label": "记住题号就行"},
                    ],
                    "correct_option": "B",
                    "rubric": "选 B",
                },
                {
                    "id": "p3",
                    "prompt": f"关于「{topic}」，你认为最关键的一步是什么？为什么？",
                    "type": "short_answer",
                    "rubric": "提到关键步骤，并有简短理由",
                },
            ],
            "mastery_prompt": f"用自己的话讲一遍：{topic} 该怎么做？",
            "reference_card_md": f"## {topic}\n\n1. 先看清问题\n2. 抓住关键一步\n3. 讲给自己听一遍\n",
            "concept_tags": [topic],
        }

    def _normalize_lesson(self, raw: Dict[str, Any], goal_text: str) -> Dict[str, Any]:
        fallback = self._mock_lesson(goal_text, None, None)
        title = str(raw.get("title") or fallback["title"]).strip()
        objective = str(raw.get("objective") or fallback["objective"]).strip()
        explanation = str(raw.get("explanation_md") or fallback["explanation_md"]).strip()
        mastery = str(raw.get("mastery_prompt") or fallback["mastery_prompt"]).strip()
        reference = str(raw.get("reference_card_md") or fallback["reference_card_md"]).strip()

        practice_raw = raw.get("practice")
        practice: List[Dict[str, Any]] = []
        if isinstance(practice_raw, list):
            for idx, item in enumerate(practice_raw[:4]):
                if not isinstance(item, dict):
                    continue
                qtype = str(item.get("type") or "short_answer").strip().lower()
                if qtype not in {"short_answer", "multiple_choice"}:
                    qtype = "short_answer"
                normalized: Dict[str, Any] = {
                    "id": str(item.get("id") or f"p{idx + 1}"),
                    "prompt": str(item.get("prompt") or "").strip() or f"练习 {idx + 1}",
                    "type": qtype,
                    "rubric": str(item.get("rubric") or "说出关键步骤").strip(),
                }
                if qtype == "multiple_choice":
                    options_raw = item.get("options") if isinstance(item.get("options"), list) else []
                    options: List[Dict[str, str]] = []
                    for opt_idx, opt in enumerate(options_raw[:4]):
                        if not isinstance(opt, dict):
                            continue
                        key = str(opt.get("key") or chr(65 + opt_idx)).strip().upper() or chr(65 + opt_idx)
                        label = str(opt.get("label") or "").strip()
                        if label:
                            options.append({"key": key, "label": label})
                    if len(options) < 2:
                        # Skip broken MCQ rather than showing empty choices
                        continue
                    correct = str(item.get("correct_option") or "").strip().upper()
                    valid_keys = {o["key"] for o in options}
                    if correct not in valid_keys:
                        correct = options[0]["key"]
                    normalized["options"] = options
                    normalized["correct_option"] = correct
                practice.append(normalized)
        if not practice:
            practice = fallback["practice"]
        # Ensure at least one short answer remains for retrieval practice
        if not any(p.get("type") == "short_answer" for p in practice):
            practice.append(fallback["practice"][-1])
        # Ensure we keep some multiple choice when model omitted them
        if not any(p.get("type") == "multiple_choice" for p in practice):
            practice = fallback["practice"][:2] + [
                p for p in practice if p.get("type") == "short_answer"
            ][:1]

        tags_raw = raw.get("concept_tags")
        tags: List[str] = []
        if isinstance(tags_raw, list):
            for tag in tags_raw[:5]:
                text = str(tag).strip()
                if text and text not in tags:
                    tags.append(text)
        if not tags:
            tags = fallback["concept_tags"]

        diagram = raw.get("diagram_mermaid")
        if diagram in {"", "null", None}:
            diagram = fallback.get("diagram_mermaid")

        return {
            "title": title,
            "objective": objective,
            "explanation_md": explanation,
            "diagram_mermaid": diagram,
            "practice": practice,
            "mastery_prompt": mastery,
            "reference_card_md": reference,
            "concept_tags": tags,
        }

    async def _call_text_json(
        self,
        *,
        prompt: str,
        channel_config: AIChannelRuntimeConfig,
        fallback: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not self._has_ai():
            return fallback
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": channel_config.model,
            "messages": [
                {"role": "system", "content": "你必须只返回 JSON，不能返回额外说明。"},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": min(int(channel_config.max_tokens or 2000), 4000),
            "temperature": float(channel_config.temperature or 0.4),
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{channel_config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code != 200:
                    logger.warning("self-directed lesson AI status=%s", response.status_code)
                    return fallback
                body = response.json()
                text = body["choices"][0]["message"]["content"]
                return self._extract_json(text) or fallback
        except Exception:
            logger.exception("self-directed lesson AI call failed")
            return fallback

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        text = text.strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return None
        return None


self_directed_lesson_service = SelfDirectedLessonService()
