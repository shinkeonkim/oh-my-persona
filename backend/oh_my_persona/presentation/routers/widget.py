from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Callable

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from ...application.abuse import AbuseService
from ...application.persona_service import PersonaService
from ...domain.repositories import ConversationRepository
from ...infrastructure.discord.bridge import DiscordBridge
from ..http_support import sse
from ..schemas import WidgetChatRequest
from ..widget_sessions import create_widget_session, verify_widget_session


def create_widget_router(
    *,
    conversations: ConversationRepository,
    persona: PersonaService,
    discord: DiscordBridge,
    enforce_limit: Callable[[Request], None],
    guard_request: Callable[[Request, str | None], str],
    abuse: AbuseService,
    verify_human: Callable[[Request, str | None], None],
) -> APIRouter:
    router = APIRouter(prefix="/api/widget")

    @router.post("/sessions", status_code=201)
    def create_session(request: Request) -> dict[str, str]:
        identity_hash = guard_request(request, None)
        conversation_id, token = create_widget_session(conversations, request.headers.get("origin"))
        abuse.bind(conversation_id, identity_hash)
        return {"conversation_id": conversation_id, "token": token}

    @router.get("/conversations/{conversation_id}")
    def get_conversation(
        conversation_id: str, x_persona_session_token: str = Header()
    ) -> dict[str, object]:
        _authorize(conversations, conversation_id, x_persona_session_token)
        return {
            "conversation_id": conversation_id,
            "messages": conversations.messages(conversation_id),
        }

    @router.get("/conversations/{conversation_id}/stream")
    async def stream_conversation(
        conversation_id: str,
        http_request: Request,
        x_persona_session_token: str = Header(),
    ) -> StreamingResponse:
        _authorize(conversations, conversation_id, x_persona_session_token)

        async def events() -> AsyncIterator[str]:
            previous = json.dumps(
                conversations.messages(conversation_id), ensure_ascii=False, sort_keys=True
            )
            idle_ticks = 0
            yield sse("ready", {"conversation_id": conversation_id})
            while not await http_request.is_disconnected():
                await asyncio.sleep(2)
                messages = await asyncio.to_thread(conversations.messages, conversation_id)
                serialized = json.dumps(messages, ensure_ascii=False, sort_keys=True)
                if serialized != previous:
                    previous, idle_ticks = serialized, 0
                    yield sse("messages", {"messages": messages})
                else:
                    idle_ticks += 1
                    if idle_ticks >= 7:
                        idle_ticks = 0
                        yield ": keepalive\n\n"

        return StreamingResponse(
            events(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @router.post("/chat")
    def chat(
        request: WidgetChatRequest,
        http_request: Request,
        background: BackgroundTasks,
    ) -> dict[str, object]:
        identity_hash = guard_request(http_request, request.conversation_id)
        verify_human(http_request, request.turnstile_token)
        enforce_limit(http_request)
        _authorize(conversations, request.conversation_id, request.token)
        abuse.bind(request.conversation_id, identity_hash)
        history = conversations.messages(request.conversation_id, 20)
        try:
            response, sources = persona.answer(request.message, request.model, history)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        conversations.append(request.conversation_id, "user", request.message)
        conversations.append(request.conversation_id, "assistant", response, request.model, sources)
        background.add_task(
            discord.mirror_exchange,
            request.conversation_id,
            request.message,
            response,
            http_request.headers.get("origin"),
        )
        return {
            "conversation_id": request.conversation_id,
            "answer": response,
            "sources": sources,
        }

    return router


def _authorize(conversations: ConversationRepository, conversation_id: str, token: str) -> None:
    if not verify_widget_session(conversations, conversation_id, token):
        raise HTTPException(status_code=401, detail="invalid widget session")
