"""
学生个人知识库 — vault 文件系统读写（claude-obsidian 结构精简版）
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


INDEX_SEED = """# 知识库目录

这里汇总你在答疑解惑中沉淀的笔记。完成答疑并写完总结后，内容会出现在这里。

"""

HOT_SEED = """# 近期学习

暂无近期答疑沉淀。

"""

LOG_SEED = """# 知识库日志

"""


class KnowledgeBaseError(Exception):
    def __init__(self, detail: str, error_code: str = "knowledge_base_error", status_code: int = 400):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(detail)


class KnowledgeBaseService:
    """按学生隔离的 Markdown vault 读写。"""

    def __init__(self, root: Optional[str] = None):
        from app.core.config import settings

        self.root = os.path.realpath(root or settings.KNOWLEDGE_BASE_ROOT)

    def student_dir(self, student_id: int) -> str:
        path = os.path.realpath(os.path.join(self.root, str(student_id)))
        if path != self.root and not path.startswith(self.root + os.sep):
            raise KnowledgeBaseError("非法学生目录。", "invalid_student_dir", status_code=400)
        return path

    def ensure_vault(self, student_id: int) -> str:
        base = self.student_dir(student_id)
        wiki = os.path.join(base, "wiki")
        for sub in ("questions", "concepts", "lessons", "learning-records", "reference"):
            os.makedirs(os.path.join(wiki, sub), exist_ok=True)
        self._write_if_missing(os.path.join(wiki, "index.md"), INDEX_SEED)
        self._write_if_missing(os.path.join(wiki, "hot.md"), HOT_SEED)
        self._write_if_missing(os.path.join(wiki, "log.md"), LOG_SEED)
        return base

    def vault_exists(self, student_id: int) -> bool:
        base = self.student_dir(student_id)
        return os.path.isdir(os.path.join(base, "wiki"))

    def resolve_note_path(self, student_id: int, rel_path: str) -> str:
        if not rel_path or rel_path.strip() == "":
            raise KnowledgeBaseError("路径不能为空。", "empty_path", status_code=400)
        normalized = rel_path.replace("\\", "/").lstrip("/")
        if ".." in normalized.split("/"):
            raise KnowledgeBaseError("非法路径。", "path_traversal", status_code=400)
        if not normalized.lower().endswith(".md"):
            raise KnowledgeBaseError("仅支持 Markdown 文件。", "invalid_extension", status_code=400)

        base = self.student_dir(student_id)
        full = os.path.realpath(os.path.join(base, normalized))
        if full != base and not full.startswith(base + os.sep):
            raise KnowledgeBaseError("非法路径。", "path_traversal", status_code=400)
        return full

    def list_notes(self, student_id: int) -> Dict[str, Any]:
        if not self.vault_exists(student_id):
            return {"items": [], "total": 0, "root_exists": False}

        base = self.student_dir(student_id)
        items: List[Dict[str, Any]] = []
        for dirpath, _, filenames in os.walk(os.path.join(base, "wiki")):
            for name in sorted(filenames):
                if not name.lower().endswith(".md"):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, base).replace("\\", "/")
                try:
                    stat = os.stat(full)
                    title = self._extract_title(full, name)
                    items.append(
                        {
                            "path": rel,
                            "title": title,
                            "size": stat.st_size,
                            "updated_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                        }
                    )
                except OSError:
                    continue

        items.sort(key=lambda x: x["path"])
        return {"items": items, "total": len(items), "root_exists": True}

    def get_note(self, student_id: int, rel_path: str) -> Dict[str, Any]:
        if not self.vault_exists(student_id):
            raise KnowledgeBaseError("知识库尚未创建。", "vault_not_found", status_code=404)
        full = self.resolve_note_path(student_id, rel_path)
        if not os.path.isfile(full):
            raise KnowledgeBaseError("笔记不存在。", "note_not_found", status_code=404)
        with open(full, "r", encoding="utf-8") as f:
            content = f.read()
        title = self._extract_title_from_text(content, os.path.basename(full))
        return {
            "path": rel_path.replace("\\", "/").lstrip("/"),
            "title": title,
            "content_markdown": content,
        }

    def write_note(self, student_id: int, rel_path: str, content: str) -> str:
        self.ensure_vault(student_id)
        full = self.resolve_note_path(student_id, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        return full

    def append_note(self, student_id: int, rel_path: str, content: str) -> str:
        self.ensure_vault(student_id)
        full = self.resolve_note_path(student_id, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "a", encoding="utf-8") as f:
            f.write(content)
        return full

    def read_text(self, student_id: int, rel_path: str) -> str:
        if not self.vault_exists(student_id):
            return ""
        try:
            full = self.resolve_note_path(student_id, rel_path)
        except KnowledgeBaseError:
            return ""
        if not os.path.isfile(full):
            return ""
        with open(full, "r", encoding="utf-8") as f:
            return f.read()

    def append_log(self, student_id: int, line: str) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        self.append_note(student_id, "wiki/log.md", f"\n- {stamp}: {line}\n")

    def update_hot(self, student_id: int, summary_block: str) -> None:
        existing = self.read_text(student_id, "wiki/hot.md") or HOT_SEED
        # Keep seed header, prepend newest block after first heading
        lines = existing.splitlines()
        header = lines[0] if lines else "# 近期学习"
        body = "\n".join(lines[1:]).strip()
        new_body = f"{summary_block.strip()}\n\n{body}".strip()
        # Cap roughly ~800 Chinese chars / ~500 words feel
        if len(new_body) > 1200:
            new_body = new_body[:1200].rstrip() + "\n\n…"
        self.write_note(student_id, "wiki/hot.md", f"{header}\n\n{new_body}\n")

    def upsert_index_entry(self, student_id: int, title: str, path: str, description: str) -> None:
        existing = self.read_text(student_id, "wiki/index.md") or INDEX_SEED
        link = f"- [[{title}]] (`{path}`) — {description}"
        if f"`{path}`" in existing:
            return
        self.write_note(student_id, "wiki/index.md", existing.rstrip() + f"\n{link}\n")

    @staticmethod
    def _write_if_missing(path: str, content: str) -> None:
        if not os.path.isfile(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    def _extract_title(self, full_path: str, filename: str) -> str:
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                text = f.read(4000)
            return self._extract_title_from_text(text, filename)
        except OSError:
            return os.path.splitext(filename)[0]

    @staticmethod
    def _extract_title_from_text(text: str, filename: str) -> str:
        body = text
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                body = text[end + 4 :]
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip() or os.path.splitext(filename)[0]
        return os.path.splitext(filename)[0]


knowledge_base_service = KnowledgeBaseService()
