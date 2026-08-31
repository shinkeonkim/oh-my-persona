from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from threading import Event

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from ...application import ChatUseCase
from ...application.persona_service import PersonaService
from ...domain.repositories import ConversationRepository
from ...infrastructure.llm.strands_agent import stream_invoke
from ..http_support import sse
from ..schemas import ChatRequest


def create_chat_router(
    *,
    use_case: ChatUseCase,
    persona: PersonaService,
    conversations: ConversationRepository,
    enforce_limit: Callable[[Request], None],
) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.post("/conversations", status_code=201)
    def create_conversation() -> dict[str, str]:
        return {"conversation_id": conversations.create()}

    @router.get("/conversations/{conversation_id}")
    def get_conversation(conversation_id: str) -> dict[str, object]:
        if not conversations.exists(conversation_id):
            raise HTTPException(status_code=404, detail="conversation not found")
        return {
            "conversation_id": conversation_id,
            "messages": conversations.messages(conversation_id),
        }

    @router.post("/chat")
    def chat(request: ChatRequest, http_request: Request) -> dict[str, object]:
        enforce_limit(http_request)
        try:
            result = use_case.execute(request.message, request.model, request.conversation_id)
        except LookupError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return {
            "conversation_id": result.conversation_id,
            "answer": result.answer,
            "sources": result.sources,
        }

    @router.post("/chat/stream")
    async def chat_stream(request: ChatRequest, http_request: Request) -> StreamingResponse:
        enforce_limit(http_request)
        conversation_id = request.conversation_id or conversations.create()
        if not conversations.exists(conversation_id):
            raise HTTPException(status_code=404, detail="conversation not found")
        history = conversations.messages(conversation_id, 20)

        async def events() -> AsyncIterator[str]:
            cancel_signal, chunks = Event(), []
            try:
                fallback, sources = await asyncio.to_thread(
                    persona.answer_context, request.message, history
                )
                yield sse("conversation", {"conversation_id": conversation_id})
                yield sse("sources", sources)
                if fallback is not None:
                    chunks.append(fallback)
                    yield sse("token", {"text": fallback})
                else:
                    async with asyncio.timeout(45):
                        async for token in stream_invoke(
                            request.message, sources, request.model, history, cancel_signal
                        ):
                            if await http_request.is_disconnected():
                                cancel_signal.set()
                                return
                            chunks.append(token)
                            yield sse("token", {"text": token})
                response = "".join(chunks)
                await asyncio.to_thread(
                    conversations.append, conversation_id, "user", request.message
                )
                await asyncio.to_thread(
                    conversations.append,
                    conversation_id,
                    "assistant",
                    response,
                    request.model,
                    sources,
                )
                yield sse("done", {})
            except TimeoutError:
                cancel_signal.set()
                yield sse(
                    "error", {"message": "답변 시간이 45초를 초과했습니다. 다시 시도해주세요."}
                )
            except Exception as error:  # noqa: BLE001
                yield sse("error", {"message": str(error)})

        return StreamingResponse(
            events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
        )

    return router
