from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from ....domain.repositories import ConversationRepository
from ...schemas import AdminConversationMessageRequest


def create_conversation_admin_router(store: ConversationRepository) -> APIRouter:
    router = APIRouter()

    @router.get("/conversations")
    def conversations(
        limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)
    ) -> dict[str, Any]:
        return {"conversations": store.list_conversations(limit, offset)}

    @router.get("/conversations/{conversation_id}")
    def conversation(conversation_id: str) -> dict[str, Any]:
        if not store.exists(conversation_id):
            raise HTTPException(status_code=404, detail="conversation not found")
        return {
            "conversation_id": conversation_id,
            "messages": store.messages(conversation_id, 500),
        }

    @router.post("/conversations/{conversation_id}/messages", status_code=201)
    def reply(conversation_id: str, request: AdminConversationMessageRequest) -> dict[str, Any]:
        if not store.exists(conversation_id):
            raise HTTPException(status_code=404, detail="conversation not found")
        store.append(conversation_id, "owner", request.content.strip())
        return store.messages(conversation_id, 1)[0]

    return router
