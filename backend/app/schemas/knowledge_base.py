"""
学生个人知识库 Schema
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class KnowledgeBaseNoteItem(BaseModel):
    path: str
    title: str
    size: int
    updated_at: datetime


class KnowledgeBaseNoteListResponse(BaseModel):
    items: List[KnowledgeBaseNoteItem] = Field(default_factory=list)
    total: int = 0
    root_exists: bool = False


class KnowledgeBaseNoteContent(BaseModel):
    path: str
    title: str
    content_markdown: str


class KnowledgeBasePriorResponse(BaseModel):
    query: str
    prior_summary: str
    has_prior: bool = False
