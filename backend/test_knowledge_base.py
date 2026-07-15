"""
学生知识库服务单测：安全路径、scaffold、ingest、空库 prior
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import unittest

from app.services.knowledge_base import KnowledgeBaseError, KnowledgeBaseService
from app.services.knowledge_ingest import KnowledgeIngestService
from app.services.knowledge_query import KnowledgeQueryService


class KnowledgeBaseServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.svc = KnowledgeBaseService(root=self._tmpdir.name)
        self.student_id = 101

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_ensure_vault_creates_structure(self) -> None:
        base = self.svc.ensure_vault(self.student_id)
        self.assertTrue(os.path.isdir(os.path.join(base, "wiki", "questions")))
        self.assertTrue(os.path.isfile(os.path.join(base, "wiki", "index.md")))
        self.assertTrue(os.path.isfile(os.path.join(base, "wiki", "hot.md")))

    def test_path_traversal_rejected(self) -> None:
        self.svc.ensure_vault(self.student_id)
        with self.assertRaises(KnowledgeBaseError) as ctx:
            self.svc.resolve_note_path(self.student_id, "../etc/passwd.md")
        self.assertEqual(ctx.exception.error_code, "path_traversal")

    def test_student_isolation_list(self) -> None:
        self.svc.ensure_vault(101)
        self.svc.write_note(101, "wiki/questions/a.md", "# A\n\nsecret for 101\n")
        self.svc.ensure_vault(202)
        listed = self.svc.list_notes(202)
        paths = [item["path"] for item in listed["items"]]
        self.assertNotIn("wiki/questions/a.md", paths)

    def test_list_and_get_note(self) -> None:
        self.svc.write_note(self.student_id, "wiki/concepts/分数.md", "# 分数\n\n先通分。\n")
        listed = self.svc.list_notes(self.student_id)
        self.assertGreaterEqual(listed["total"], 1)
        note = self.svc.get_note(self.student_id, "wiki/concepts/分数.md")
        self.assertEqual(note["title"], "分数")
        self.assertIn("通分", note["content_markdown"])


class KnowledgeIngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.kb = KnowledgeBaseService(root=self._tmpdir.name)
        # Patch singleton used by ingest
        import app.services.knowledge_ingest as ingest_mod
        import app.services.knowledge_base as kb_mod

        self._old_kb = kb_mod.knowledge_base_service
        kb_mod.knowledge_base_service = self.kb
        ingest_mod.knowledge_base_service = self.kb
        self.ingest = KnowledgeIngestService()
        self.student_id = 303

    def tearDown(self) -> None:
        import app.services.knowledge_ingest as ingest_mod
        import app.services.knowledge_base as kb_mod

        kb_mod.knowledge_base_service = self._old_kb
        ingest_mod.knowledge_base_service = self._old_kb
        self._tmpdir.cleanup()

    def test_ingest_creates_question_and_hot(self) -> None:
        path = self.ingest.ingest_from_self_study_session(
            self.student_id,
            session_id=42,
            summary_before="我忘了分数加法要先通分",
            summary_after="现在知道要先通分再相加",
            problem_text="计算 1/2 + 1/3",
            primary_error_type="relation_error",
            ai_guidance_summary=["先问问分母是否相同", "再提示通分"],
        )
        self.assertTrue(path.startswith("wiki/questions/"))
        note = self.kb.get_note(self.student_id, path)
        self.assertIn("通分", note["content_markdown"])
        hot = self.kb.read_text(self.student_id, "wiki/hot.md")
        self.assertIn("会话 #42", hot)
        concepts = self.kb.list_notes(self.student_id)
        concept_paths = [i["path"] for i in concepts["items"] if i["path"].startswith("wiki/concepts/")]
        self.assertTrue(any("分数" in p or "数量关系" in p for p in concept_paths))


class KnowledgeQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.kb = KnowledgeBaseService(root=self._tmpdir.name)
        import app.services.knowledge_query as query_mod
        import app.services.knowledge_base as kb_mod
        import app.services.knowledge_ingest as ingest_mod

        self._old_kb = kb_mod.knowledge_base_service
        kb_mod.knowledge_base_service = self.kb
        query_mod.knowledge_base_service = self.kb
        ingest_mod.knowledge_base_service = self.kb
        self.query = KnowledgeQueryService()
        self.ingest = KnowledgeIngestService()
        self.student_id = 404

    def tearDown(self) -> None:
        import app.services.knowledge_query as query_mod
        import app.services.knowledge_base as kb_mod
        import app.services.knowledge_ingest as ingest_mod

        kb_mod.knowledge_base_service = self._old_kb
        query_mod.knowledge_base_service = self._old_kb
        ingest_mod.knowledge_base_service = self._old_kb
        self._tmpdir.cleanup()

    def test_empty_vault_returns_empty_prior(self) -> None:
        summary = asyncio.run(
            self.query.query_prior_knowledge(None, self.student_id, "分数加法怎么做")  # type: ignore[arg-type]
        )
        self.assertEqual(summary, "")

    def test_prior_after_ingest(self) -> None:
        self.ingest.ingest_from_self_study_session(
            self.student_id,
            session_id=7,
            summary_before="不会通分",
            summary_after="分数加法要先通分",
            problem_text="1/2+1/4",
        )
        summary = asyncio.run(
            self.query.query_prior_knowledge(None, self.student_id, "这道分数加法我又不会了")  # type: ignore[arg-type]
        )
        self.assertTrue(summary)
        self.assertIn("知识库", summary)


if __name__ == "__main__":
    unittest.main()
