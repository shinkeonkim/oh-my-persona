from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from ....domain.repositories import KnowledgeRepository
from ....infrastructure.files import read_jsonl
from ...http_support import knowledge_values, packaged_chunk
from ...schemas import KnowledgeRequest


def create_knowledge_admin_router(root: Path, store: KnowledgeRepository) -> APIRouter:
    router = APIRouter()

    @router.get("/knowledge")
    def list_knowledge(
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        packaged_limit: int = Query(50, ge=1, le=200),
        packaged_offset: int = Query(0, ge=0),
        q: str | None = Query(None, max_length=200),
        source_id: str | None = Query(None, max_length=100),
    ) -> dict[str, Any]:
        chunks = read_jsonl(root / "data/processed/chunks.jsonl")
        sources = {
            item["source_id"]: item for item in read_jsonl(root / "data/registry/sources.jsonl")
        }
        query = (q or "").casefold()
        filtered = [
            item
            for item in chunks
            if (not source_id or item.get("source_id") == source_id)
            and (
                not query
                or query
                in " ".join(
                    (
                        item.get("text", ""),
                        item.get("source_path", ""),
                        item.get("source_id", ""),
                        item.get("document_id", ""),
                    )
                ).casefold()
            )
        ]
        facets = sorted(
            {
                (item.get("source_id"), sources.get(item.get("source_id", ""), {}).get("title"))
                for item in chunks
                if item.get("source_id")
            }
        )
        return {
            "managed": store.list(limit, offset),
            "packaged": [
                packaged_chunk(item, sources.get(item.get("source_id", ""), {}))
                for item in filtered[packaged_offset : packaged_offset + packaged_limit]
            ],
            "packaged_total": len(filtered),
            "packaged_unfiltered_total": len(chunks),
            "packaged_offset": packaged_offset,
            "packaged_limit": packaged_limit,
            "source_facets": [{"source_id": key, "title": title} for key, title in facets],
        }

    @router.get("/chunks/{chunk_id}")
    def get_chunk(chunk_id: str) -> dict[str, Any]:
        chunk = next(
            (
                item
                for item in read_jsonl(root / "data/processed/chunks.jsonl")
                if item["chunk_id"] == chunk_id
            ),
            None,
        )
        if not chunk:
            raise HTTPException(status_code=404, detail="chunk not found")
        source = next(
            (
                item
                for item in read_jsonl(root / "data/registry/sources.jsonl")
                if item["source_id"] == chunk.get("source_id")
            ),
            {},
        )
        return packaged_chunk(chunk, source)

    @router.post("/knowledge", status_code=201)
    def create_knowledge(request: KnowledgeRequest) -> dict[str, Any]:
        return store.create(knowledge_values(request))

    @router.put("/knowledge/{item_id}")
    def update_knowledge(item_id: str, request: KnowledgeRequest) -> dict[str, Any]:
        item = store.update(item_id, knowledge_values(request))
        if not item:
            raise HTTPException(status_code=404, detail="knowledge not found")
        return item

    @router.delete("/knowledge/{item_id}", status_code=204)
    def delete_knowledge(item_id: str) -> None:
        if not store.delete(item_id):
            raise HTTPException(status_code=404, detail="knowledge not found")

    return router
