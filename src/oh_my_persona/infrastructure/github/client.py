from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from ...domain.privacy import SENSITIVE_PATTERNS


def rest(endpoint: str, fields: dict[str, str] | None = None, paginate: bool = False) -> Any:
    command = ["gh", "api", "-X", "GET"]
    if paginate:
        command.extend(("--paginate", "--slurp"))
    command.append(endpoint)
    for key, value in (fields or {}).items():
        command.extend(("-f", f"{key}={value}"))
    for attempt in range(4):
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        if "HTTP 404" in result.stderr or "HTTP 409" in result.stderr:
            return None
        if attempt < 3:
            time.sleep(2**attempt)
    raise RuntimeError(f"GitHub API request failed for {endpoint}: {result.stderr.strip()}")


def graphql(query: str, fields: dict[str, str]) -> dict[str, Any]:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in fields.items():
        command.extend(("-F", f"{key}={value}"))
    for attempt in range(4):
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode == 0:
            data: dict[str, Any] = json.loads(result.stdout)["data"]
            return data
        if attempt < 3:
            time.sleep(2**attempt)
    raise RuntimeError(f"GitHub GraphQL request failed: {result.stderr.strip()}")


def is_safe(text: str) -> bool:
    return not any(pattern.search(text) for pattern in SENSITIVE_PATTERNS.values())


def record_document(
    root: Path,
    source: dict[str, Any],
    relative: str,
    content: str,
    canonical_url: str,
    observed_at: str,
    published_at: str | None,
    commit_sha: str | None,
    extractor: str,
) -> dict[str, Any]:
    digest = hashlib.sha256(content.encode()).hexdigest()
    raw = root / "data/raw" / source["source_id"] / relative
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(content, encoding="utf-8")
    return {
        "document_id": f"DOC-{digest[:20]}",
        "source_id": source["source_id"],
        "canonical_url": canonical_url,
        "repository_url": source["canonical_url"],
        "commit_sha": commit_sha,
        "relative_path": relative,
        "raw_path": str(raw.relative_to(root)),
        "content_sha256": digest,
        "mime_type": "text/markdown" if relative.endswith(".md") else "text/plain",
        "published_at": published_at,
        "observed_at": observed_at,
        "extractor_version": extractor,
        "status": "accepted",
    }


def write_manifest(path: Path, documents: list[dict[str, Any]]) -> None:
    documents.sort(key=lambda item: (item["source_id"], item["relative_path"]))
    path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in documents), encoding="utf-8"
    )


def write_report(path: Path, observed_at: str, values: dict[str, Any]) -> None:
    path.write_text(
        json.dumps({"observed_at": observed_at, **values}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
