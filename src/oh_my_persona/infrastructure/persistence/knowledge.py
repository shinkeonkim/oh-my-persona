from __future__ import annotations

from ...domain.repositories import KnowledgeQuestionRepository, KnowledgeRepository
from .knowledge_memory import MemoryKnowledgeQuestionStore, MemoryKnowledgeStore
from .knowledge_postgres import PostgresKnowledgeQuestionStore, PostgresKnowledgeStore


def KnowledgeStore(database_url: str | None = None) -> KnowledgeRepository:
    return PostgresKnowledgeStore(database_url) if database_url else MemoryKnowledgeStore()


def KnowledgeQuestionStore(database_url: str | None = None) -> KnowledgeQuestionRepository:
    if database_url:
        return PostgresKnowledgeQuestionStore(database_url)
    return MemoryKnowledgeQuestionStore()


__all__ = ["KnowledgeQuestionStore", "KnowledgeStore"]
