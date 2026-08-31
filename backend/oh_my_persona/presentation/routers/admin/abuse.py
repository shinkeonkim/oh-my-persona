from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from ....application.abuse import AbuseService
from ....domain.abuse import BlockDuration
from ...schemas import AbuseBlockRequest


def create_abuse_admin_router(abuse: AbuseService) -> APIRouter:
    router = APIRouter()

    @router.get("/abuse/blocks")
    def blocks() -> dict[str, Any]:
        return {"blocks": abuse.list_blocks()}

    @router.post("/conversations/{conversation_id}/blocks", status_code=201)
    def block_conversation(
        conversation_id: str, request: AbuseBlockRequest
    ) -> dict[str, object]:
        duration = BlockDuration(request.duration)
        try:
            if request.scope == "identity":
                block = abuse.block_identity_for_conversation(
                    conversation_id, duration, request.reason, request.note
                )
            else:
                block = abuse.block_conversation(
                    conversation_id, duration, request.reason, request.note
                )
        except LookupError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        return block.as_dict()

    @router.delete("/abuse/blocks/{block_id}")
    def unblock(block_id: str) -> dict[str, object]:
        try:
            return abuse.revoke(block_id).as_dict()
        except LookupError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    return router
