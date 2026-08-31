from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ..application.persona_service import PersonaService
from ..domain.repositories import (
    ConversationRepository,
    KnowledgeQuestionRepository,
    KnowledgeRepository,
)
from ..infrastructure.discord.bridge import DiscordBridge
from ..infrastructure.llm.strands_agent import invoke
from ..infrastructure.persistence.conversations import ConversationStore, RateLimiter
from ..infrastructure.persistence.knowledge import KnowledgeQuestionStore, KnowledgeStore
from ..infrastructure.retrieval import MemoryRetriever


@dataclass(frozen=True, slots=True)
class Container:
    root: Path
    conversations: ConversationRepository
    knowledge: KnowledgeRepository
    knowledge_questions: KnowledgeQuestionRepository
    persona: PersonaService
    rate_limiter: RateLimiter
    discord: DiscordBridge


def create_container() -> Container:
    root = _root_path()
    database_url = os.environ.get("PERSONA_DATABASE_URL")
    conversations = ConversationStore(database_url)
    knowledge = KnowledgeStore(database_url)
    questions = KnowledgeQuestionStore(database_url)
    generator = None
    if os.environ.get("PERSONA_LITELLM_URL") and os.environ.get("PERSONA_LITELLM_KEY"):
        generator = lambda question, hits, model, history: (
            invoke(question, hits, model, history),
            hits,
        )
    persona = PersonaService(MemoryRetriever(root), knowledge, generator)
    return Container(
        root=root,
        conversations=conversations,
        knowledge=knowledge,
        knowledge_questions=questions,
        persona=persona,
        rate_limiter=RateLimiter(conversations),
        discord=DiscordBridge(conversations),
    )


def _root_path() -> Path:
    configured = os.environ.get("PERSONA_ROOT")
    if configured:
        return Path(configured).resolve()
    return Path(__file__).resolve().parents[3]
