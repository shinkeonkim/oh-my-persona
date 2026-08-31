from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from ...domain.chunks import chunk_text
from ...support import read_jsonl


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme != "https" or not parts.netloc:
        raise ValueError(f"public source URL must be absolute HTTPS: {url}")
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(("https", parts.netloc.lower(), path, parts.query, ""))


def iter_corpus_files(root: Path) -> Iterable[Path]:
    for directory in (root / "data" / "raw", root / "data" / "curated", root / "docs"):
        if directory.exists():
            yield from sorted(
                path for path in directory.rglob("*") if path.suffix in {".md", ".txt"}
            )


def build_chunks(root: Path, max_chars: int = 750) -> list[dict[str, Any]]:
    """Build traceable chunks from registered snapshots and authored project docs."""
    output: list[dict[str, Any]] = []
    seen_content: set[str] = set()
    documents = read_jsonl(root / "data/registry/documents.jsonl")
    registered_paths: set[str] = set()
    for document in documents:
        path = root / document["raw_path"]
        if document.get("status") != "accepted" or not path.exists():
            continue
        registered_paths.add(str(path.resolve()))
        for chunk in chunk_text(
            path.read_text(encoding="utf-8", errors="replace"), document["raw_path"], max_chars
        ):
            if chunk.content_sha256 in seen_content:
                continue
            seen_content.add(chunk.content_sha256)
            item = chunk.as_dict()
            item.update(
                {
                    key: document.get(key)
                    for key in (
                        "document_id",
                        "source_id",
                        "canonical_url",
                        "commit_sha",
                        "observed_at",
                    )
                }
            )
            output.append(item)
    for path in iter_corpus_files(root):
        if str(path.resolve()) in registered_paths:
            continue
        for chunk in chunk_text(
            path.read_text(encoding="utf-8", errors="replace"),
            str(path.relative_to(root)),
            max_chars,
        ):
            if chunk.content_sha256 in seen_content:
                continue
            seen_content.add(chunk.content_sha256)
            output.append(chunk.as_dict())
    return output


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    sources = read_jsonl(root / "data/registry/sources.jsonl")
    claims = read_jsonl(root / "data/curated/claims.jsonl")
    source_ids = {item.get("source_id") for item in sources}
    if len(source_ids) != len(sources):
        errors.append("source_id values must be unique")
    for source in sources:
        try:
            canonicalize_url(source.get("canonical_url", ""))
        except ValueError as error:
            errors.append(f"{source.get('source_id')}: {error}")
        if not source.get("observed_at"):
            errors.append(f"{source.get('source_id')}: observed_at is required")
    claim_ids = {item.get("claim_id") for item in claims}
    if len(claim_ids) != len(claims):
        errors.append("claim_id values must be unique")
    for claim in claims:
        missing = set(claim.get("source_ids", [])) - source_ids
        if missing:
            errors.append(f"{claim.get('claim_id')}: unknown sources {sorted(missing)}")
        if "date_precision" not in claim:
            errors.append(f"{claim.get('claim_id')}: date_precision is required")
    return errors
