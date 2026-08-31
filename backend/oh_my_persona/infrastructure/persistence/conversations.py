from __future__ import annotations

import os

from ...domain.repositories import ConversationRepository
from .conversation_memory import MemoryConversationStore
from .conversation_postgres import PostgresConversationStore
from .rate_limit import RateLimiter


def ConversationStore(database_url: str | None = None) -> ConversationRepository:
    configured = database_url or os.environ.get("PERSONA_DATABASE_URL")
    return PostgresConversationStore(configured) if configured else MemoryConversationStore()


__all__ = ["ConversationStore", "RateLimiter"]
