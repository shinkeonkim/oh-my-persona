from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from ...application.persona_service import PersonaService
from ...domain.repositories import KnowledgeRepository
from ...infrastructure.files import read_jsonl
from ...infrastructure.llm.strands_agent import ALLOWED_MODELS


def create_public_router(
    *,
    root: Path,
    static: Path,
    frontend_dist: Path,
    persona: PersonaService,
    knowledge: KnowledgeRepository,
) -> APIRouter:
    router = APIRouter()

    def spa() -> FileResponse:
        return FileResponse(frontend_dist / "index.html")

    @router.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return spa()

    @router.get("/admin", include_in_schema=False)
    def admin_index() -> FileResponse:
        return spa()

    @router.get("/sdk/persona-widget.js", include_in_schema=False)
    def widget_sdk() -> FileResponse:
        return FileResponse(
            static / "persona-widget.js",
            media_type="text/javascript",
            headers={"Cache-Control": "no-cache, must-revalidate"},
        )

    @router.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/api/models")
    def models() -> dict[str, tuple[str, ...]]:
        return {"models": ALLOWED_MODELS}

    @router.get("/api/search")
    def search_api(
        q: str = Query(min_length=1, max_length=4000), limit: int = Query(6, ge=1, le=20)
    ) -> dict[str, object]:
        return {"query": q, "hits": persona.search(q, limit)}

    @router.get("/api/sources/{source_id}")
    def source_api(source_id: str) -> dict[str, object]:
        source = next(
            (
                item
                for item in read_jsonl(root / "data/registry/sources.jsonl")
                if item["source_id"] == source_id
            ),
            None,
        )
        if not source or source.get("status") not in {"accepted", "review"}:
            raise HTTPException(status_code=404, detail="source not found")
        return source

    @router.get("/api/knowledge/{item_id}")
    def managed_knowledge(item_id: str) -> dict[str, object]:
        item = knowledge.get(item_id)
        if not item or item["status"] != "active":
            raise HTTPException(status_code=404, detail="knowledge not found")
        return item

    return router
