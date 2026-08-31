from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..files import read_jsonl
from .client import graphql as _graphql
from .client import is_safe as _safe
from .client import record_document as _record
from .client import rest as _gh


def select_document_paths(tree: list[dict[str, Any]], limit: int = 40) -> list[str]:
    keywords = {
        "architecture",
        "changelog",
        "contributing",
        "design",
        "roadmap",
        "security",
        "setup",
    }
    candidates: list[tuple[int, str]] = []
    for item in tree:
        path = item.get("path", "")
        lowered = path.lower()
        if item.get("type") != "blob" or not lowered.endswith((".md", ".mdx", ".rst", ".txt")):
            continue
        name = Path(lowered).name
        if name.startswith("readme."):
            continue
        parts = Path(lowered).parts
        in_docs = any(part in {"doc", "docs", "documentation", ".github"} for part in parts[:-1])
        named_doc = any(word in Path(name).stem for word in keywords)
        if not (len(parts) == 1 or in_docs or named_doc):
            continue
        priority = 0 if in_docs else 1 if named_doc else 2
        candidates.append((priority, path))
    return [path for _, path in sorted(candidates)[:limit]]


def _fetch_blobs(owner: str, name: str, commit: str, paths: list[str]) -> dict[str, dict[str, Any]]:
    blobs: dict[str, dict[str, Any]] = {}
    for offset in range(0, len(paths), 20):
        batch = paths[offset : offset + 20]
        fields = "\n".join(
            f"b{index}: object(expression:{json.dumps(f'{commit}:{path}')}) "
            "{ ... on Blob { oid byteSize text } }"
            for index, path in enumerate(batch)
        )
        query = (
            "query { repository(owner:"
            + json.dumps(owner)
            + ", name:"
            + json.dumps(name)
            + ") {\n"
            + fields
            + "\n} }"
        )
        repository = _graphql(query, {})["repository"]
        for index, path in enumerate(batch):
            if repository.get(f"b{index}"):
                blobs[path] = repository[f"b{index}"]
    return blobs


def collect_public_docs(root: Path) -> dict[str, int]:
    inventory = json.loads(
        (root / "data/research/github-repositories.json").read_text(encoding="utf-8")
    )
    source_by_url = {
        item["canonical_url"].rstrip("/"): item
        for item in read_jsonl(root / "data/registry/sources.jsonl")
    }
    manifest_path = root / "data/registry/documents.jsonl"
    documents = [
        item
        for item in read_jsonl(manifest_path)
        if not item.get("relative_path", "").startswith("github-docs/")
    ]
    observed_at = datetime.now(UTC).isoformat()
    stats = {
        "repositories": 0,
        "repositories_with_docs": 0,
        "documents": 0,
        "oversized": 0,
        "rejected": 0,
    }

    for repo in inventory["repositories"]:
        branch = repo.get("defaultBranchRef") or {}
        target = branch.get("target") or {}
        commit = target.get("oid")
        if not commit:
            continue
        stats["repositories"] += 1
        full_name = repo["nameWithOwner"]
        tree_response = _gh(f"repos/{full_name}/git/trees/{commit}", {"recursive": "1"})
        if not tree_response:
            continue
        paths = select_document_paths(tree_response.get("tree", []))
        if not paths:
            continue
        owner, name = full_name.split("/", 1)
        blobs = _fetch_blobs(owner, name, commit, paths)
        accepted_for_repo = 0
        source = source_by_url[repo["url"].rstrip("/")]
        for path in paths:
            blob = blobs.get(path) or {}
            text = blob.get("text")
            if text is None or blob.get("byteSize", 0) > 1_000_000:
                stats["oversized"] += 1
                continue
            if not _safe(text):
                stats["rejected"] += 1
                continue
            relative = f"github-docs/{path}"
            canonical = f"{repo['url']}/blob/{commit}/{quote(path)}"
            documents.append(
                _record(
                    root,
                    source,
                    relative,
                    text,
                    canonical,
                    observed_at,
                    repo.get("updatedAt"),
                    commit,
                    "github-public-doc-v1",
                )
            )
            accepted_for_repo += 1
            stats["documents"] += 1
        if accepted_for_repo:
            stats["repositories_with_docs"] += 1

    documents.sort(key=lambda item: (item["source_id"], item["relative_path"]))
    manifest_path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in documents), encoding="utf-8"
    )
    report = root / "data/research/github-public-docs.json"
    report.write_text(
        json.dumps({"observed_at": observed_at, **stats}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return stats
