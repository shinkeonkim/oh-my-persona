from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ingest import MAX_FILE_BYTES, SENSITIVE_PATTERNS

TEXT_SUFFIXES = {
    ".md",
    ".markdown",
    ".txt",
    ".ts",
    ".tsx",
    ".js",
    ".vue",
    ".json",
    ".html",
    ".css",
    ".xml",
    ".py",
    ".sql",
}
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "coverage",
    ".astro",
    ".cache",
    "test-results",
}
EXCLUDED_NAMES = {"package-lock.json", "bun.lock", "bun.lockb", "uv.lock"}


def git_value(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def collect_local_repository(root: Path, repo: Path, source: dict[str, Any]) -> dict[str, int]:
    repo = repo.resolve()
    commit = git_value(repo, "rev-parse", "HEAD")
    tracked = git_value(repo, "ls-files", "-z").split("\0")
    destination_root = root / "data/raw" / source["source_id"]
    manifest_path = root / "data/registry/documents.jsonl"
    existing = _read_jsonl(manifest_path)
    retained = [item for item in existing if item.get("source_id") != source["source_id"]]
    observed_at = datetime.now(UTC).isoformat()
    accepted = rejected = duplicates = 0
    seen_hashes: set[str] = set()
    records: list[dict[str, Any]] = []

    for relative_text in tracked:
        if not relative_text:
            continue
        relative = Path(relative_text)
        path = repo / relative
        if (
            any(part in EXCLUDED_PARTS for part in relative.parts)
            or relative.name in EXCLUDED_NAMES
        ):
            continue
        if (
            path.suffix.lower() not in TEXT_SUFFIXES
            or not path.is_file()
            or path.stat().st_size > MAX_FILE_BYTES
        ):
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        reasons = [name for name, pattern in SENSITIVE_PATTERNS.items() if pattern.search(content)]
        if reasons:
            rejected += 1
            continue
        digest = hashlib.sha256(content.encode()).hexdigest()
        if digest in seen_hashes:
            duplicates += 1
            continue
        seen_hashes.add(digest)
        destination = destination_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        blob_url = f"{source['canonical_url']}/blob/{commit}/{relative.as_posix()}"
        records.append(
            {
                "document_id": f"DOC-{digest[:20]}",
                "source_id": source["source_id"],
                "canonical_url": blob_url,
                "repository_url": source["canonical_url"],
                "commit_sha": commit,
                "relative_path": relative.as_posix(),
                "raw_path": str(destination.relative_to(root)),
                "content_sha256": digest,
                "mime_type": _mime(path),
                "observed_at": observed_at,
                "extractor_version": "local-git-v1",
                "status": "accepted",
            }
        )
        accepted += 1

    history = git_value(
        repo,
        "log",
        "--all",
        "--date=iso-strict",
        "--pretty=format:%H%x00%aI%x00%s%x1e",
    )
    for entry in history.split("\x1e"):
        entry = entry.strip()
        if not entry:
            continue
        commit_sha, authored_at, subject = entry.split("\x00", 2)
        subject = " ".join(subject.split())
        content = (
            f"GitHub repository: {source['canonical_url']}\n"
            f"Commit date: {authored_at}\n"
            f"Commit: {subject}\n"
        )
        reasons = [name for name, pattern in SENSITIVE_PATTERNS.items() if pattern.search(content)]
        if reasons:
            rejected += 1
            continue
        digest = hashlib.sha256(content.encode()).hexdigest()
        if digest in seen_hashes:
            duplicates += 1
            continue
        seen_hashes.add(digest)
        relative = Path(".history") / f"{commit_sha}.txt"
        destination = destination_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        records.append(
            {
                "document_id": f"DOC-{digest[:20]}",
                "source_id": source["source_id"],
                "canonical_url": f"{source['canonical_url']}/commit/{commit_sha}",
                "repository_url": source["canonical_url"],
                "commit_sha": commit_sha,
                "relative_path": relative.as_posix(),
                "raw_path": str(destination.relative_to(root)),
                "content_sha256": digest,
                "mime_type": "text/plain",
                "published_at": authored_at,
                "observed_at": observed_at,
                "extractor_version": "local-git-history-v1",
                "status": "accepted",
            }
        )
        accepted += 1

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    all_records = sorted(
        retained + records, key=lambda item: (item["source_id"], item["relative_path"])
    )
    manifest_path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in all_records),
        encoding="utf-8",
    )
    return {"accepted": accepted, "rejected": rejected, "duplicates": duplicates}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _mime(path: Path) -> str:
    return {
        ".md": "text/markdown",
        ".vue": "text/x-vue",
        ".json": "application/json",
        ".xml": "application/xml",
    }.get(path.suffix.lower(), "text/plain")
