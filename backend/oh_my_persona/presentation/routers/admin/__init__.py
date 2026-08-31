from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from fastapi import APIRouter, Depends

from ....application.abuse import AbuseService
from ....domain.repositories import (
    ConversationRepository,
    KnowledgeQuestionRepository,
    KnowledgeRepository,
)
from .abuse import create_abuse_admin_router
from .conversations import create_conversation_admin_router
from .gaps import create_gap_admin_router
from .knowledge import create_knowledge_admin_router


def create_admin_router(
    *,
    root: Path,
    knowledge_store: KnowledgeRepository,
    question_store: KnowledgeQuestionRepository,
    conversation_store: ConversationRepository,
    authenticate: Callable[..., None],
    abuse: AbuseService,
) -> APIRouter:
    router = APIRouter(prefix="/api/admin", dependencies=[Depends(authenticate)])
    router.include_router(create_knowledge_admin_router(root, knowledge_store))
    router.include_router(create_gap_admin_router(root, knowledge_store, question_store))
    router.include_router(create_conversation_admin_router(conversation_store, abuse))
    router.include_router(create_abuse_admin_router(abuse))
    return router


__all__ = ["create_admin_router"]
