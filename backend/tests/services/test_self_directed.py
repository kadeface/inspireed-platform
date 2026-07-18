"""
自主学习微课生成与知识库入库单测（不依赖真实 LLM）
"""

from __future__ import annotations

import tempfile
import unittest

from app.services.knowledge_base import KnowledgeBaseService
from app.services.knowledge_ingest import KnowledgeIngestService
from app.services.mathlab_curriculum import MathLabCurriculumIndex
from app.services.self_directed_lesson import SelfDirectedLessonService


class MathLabCurriculumSearchTests(unittest.TestCase):
    def test_circle_robot_goal_hits_draw_circle_task(self) -> None:
        index = MathLabCurriculumIndex()
        matches = index.search("轮式机器人虚拟仿真走圆形", limit=3)
        self.assertTrue(matches)
        ids = [m["id"] for m in matches]
        # 小学画圆 / 初中圆形巡检 至少命中其一
        self.assertTrue(
            any(i in ids for i in ("p6t23",))
            or any("圆" in (m.get("title") or "") for m in matches)
        )
        top = matches[0]
        self.assertIn("mathlab_url", top)
        self.assertTrue(top["mathlab_url"].startswith("/mathlab/index.html?task="))

    def test_mock_lesson_grounds_in_curriculum(self) -> None:
        svc = SelfDirectedLessonService()
        index = MathLabCurriculumIndex()
        matches = index.search("轮式机器人画圆", limit=2)
        self.assertTrue(matches)
        lesson = svc._mock_lesson("轮式机器人画圆", None, matches)
        self.assertIn(matches[0]["id"], lesson["explanation_md"])
        self.assertIn("/mathlab/index.html?task=", lesson["explanation_md"])
        self.assertNotIn("先别急着做很多题", lesson["explanation_md"])


class SelfDirectedLessonNormalizeTests(unittest.TestCase):
    def test_normalize_fills_defaults(self) -> None:
        svc = SelfDirectedLessonService()
        lesson = svc._normalize_lesson({"title": "通分"}, "分数加法")
        self.assertEqual(lesson["title"], "通分")
        self.assertTrue(lesson["practice"])
        types = [p["type"] for p in lesson["practice"]]
        self.assertIn("multiple_choice", types)
        self.assertIn("short_answer", types)
        self.assertTrue(lesson["mastery_prompt"])

    def test_grade_multiple_choice(self) -> None:
        svc = SelfDirectedLessonService()
        item = {
            "type": "multiple_choice",
            "correct_option": "B",
            "options": [
                {"key": "A", "label": "错的"},
                {"key": "B", "label": "对的"},
            ],
        }
        ok = svc._grade_multiple_choice(item, "B")
        bad = svc._grade_multiple_choice(item, "A")
        self.assertTrue(ok["ok"])
        self.assertFalse(bad["ok"])
        self.assertIn("B", bad["feedback"])


class SelfDirectedIngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.kb = KnowledgeBaseService(root=self._tmpdir.name)
        import app.services.knowledge_base as kb_mod
        import app.services.knowledge_ingest as ingest_mod

        self._old = kb_mod.knowledge_base_service
        kb_mod.knowledge_base_service = self.kb
        ingest_mod.knowledge_base_service = self.kb
        self.ingest = KnowledgeIngestService()

    def tearDown(self) -> None:
        import app.services.knowledge_base as kb_mod
        import app.services.knowledge_ingest as ingest_mod

        kb_mod.knowledge_base_service = self._old
        ingest_mod.knowledge_base_service = self._old
        self._tmpdir.cleanup()

    def test_ingest_writes_lesson_and_record(self) -> None:
        path = self.ingest.ingest_from_self_directed_session(
            501,
            session_id=9,
            goal_text="分数加法",
            mission_why="作业总卡在通分",
            lesson={
                "title": "分数加法：先通分",
                "objective": "能说出通分步骤",
                "explanation_md": "先通分再相加",
                "reference_card_md": "## 口诀\n先通分",
                "concept_tags": ["分数加法", "通分"],
            },
            mastery_answer="异分母要先通分再加",
        )
        self.assertTrue(path.startswith("wiki/lessons/"))
        note = self.kb.get_note(501, path)
        self.assertIn("通分", note["content_markdown"])
        listed = self.kb.list_notes(501)
        paths = [i["path"] for i in listed["items"]]
        self.assertTrue(any(p.startswith("wiki/learning-records/") for p in paths))
        self.assertTrue(any(p.startswith("wiki/reference/") for p in paths))


if __name__ == "__main__":
    unittest.main()
