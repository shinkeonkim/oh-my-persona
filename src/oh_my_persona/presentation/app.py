"""FastAPI application composition root."""

from __future__ import annotations

import asyncio
import os
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ..application import ChatUseCase
from ..bootstrap.container import create_container
from .http_support import enforce_rate_limit
from .routers import create_chat_router, create_public_router, create_widget_router
from .routers.admin import create_admin_router

container = create_container()
ROOT = container.root
STATIC = ROOT / "static"
FRONTEND_DIST = ROOT / "frontend" / "dist"
store = container.conversations
knowledge_store = container.knowledge
knowledge_question_store = container.knowledge_questions
limiter = container.rate_limiter
discord_bridge = container.discord
persona = container.persona
chat_use_case = ChatUseCase(store, persona.answer)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await asyncio.gather(
        asyncio.to_thread(store.initialize),
        asyncio.to_thread(knowledge_store.initialize),
        asyncio.to_thread(knowledge_question_store.initialize),
    )
    yield


def require_admin(authorization: str | None = Header(default=None)) -> None:
    expected = os.environ.get("PERSONA_ADMIN_TOKEN")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not expected:
        raise HTTPException(status_code=503, detail="admin access is not configured")
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="invalid admin token")


def _enforce_rate_limit(request: Request) -> None:
    enforce_rate_limit(request, limiter)


def create_app() -> FastAPI:
    application = FastAPI(title="oh-my-persona", version="0.3.0", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://portfolio.shinkeonkim.com",
            "https://resume.shinkeonkim.com",
            "http://localhost:4173",
            "http://localhost:5173",
        ],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Persona-Session-Token"],
    )
    application.mount("/static", StaticFiles(directory=STATIC), name="static")
    if FRONTEND_DIST.is_dir():
        application.mount(
            "/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="frontend-assets"
        )
    application.include_router(
        create_public_router(
            root=ROOT,
            static=STATIC,
            frontend_dist=FRONTEND_DIST,
            persona=persona,
            knowledge=knowledge_store,
        )
    )
    application.include_router(
        create_chat_router(
            use_case=chat_use_case,
            persona=persona,
            conversations=store,
            enforce_limit=_enforce_rate_limit,
        )
    )
    application.include_router(
        create_widget_router(
            conversations=store,
            persona=persona,
            discord=discord_bridge,
            enforce_limit=_enforce_rate_limit,
        )
    )
    application.include_router(
        create_admin_router(
            root=ROOT,
            knowledge_store=knowledge_store,
            question_store=knowledge_question_store,
            conversation_store=store,
            authenticate=require_admin,
        )
    )
    return application


app = create_app()
