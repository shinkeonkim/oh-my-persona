from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..collect import EXCLUDED_NAMES, EXCLUDED_PARTS, TEXT_SUFFIXES
from ..corpus import read_jsonl
from .github_support import is_safe as _safe
from .github_support import record_document as _record


def _line_count(path: Path, header_lines: int = 3) -> int:
    if not path.exists():
        return 0
    return max(
        0, len(path.read_text(encoding="utf-8", errors="replace").splitlines()) - header_lines
    )


def collect_priority_trees(root: Path, limit: int = 30) -> dict[str, Any]:
    inventory = json.loads(
        (root / "data/research/github-repositories.json").read_text(encoding="utf-8")
    )
    source_by_url = {
        item["canonical_url"].rstrip("/"): item
        for item in read_jsonl(root / "data/registry/sources.jsonl")
    }
    ranked: list[tuple[int, str, dict[str, Any], int, int]] = []
    for repo in inventory["repositories"]:
        if "contributor" not in repo["relations"]:
            continue
        source = source_by_url[repo["url"].rstrip("/")]
        raw = root / "data/raw" / source["source_id"]
        commits = _line_count(raw / "github-authored-commits.txt")
        prs = _line_count(raw / "github-authored-pull-requests.txt")
        score = commits * 5 + prs * 10
        if score:
            ranked.append((score, repo["nameWithOwner"].lower(), repo, commits, prs))
    selected = sorted(ranked, key=lambda item: (-item[0], item[1]))[:limit]

    manifest_path = root / "data/registry/documents.jsonl"
    documents = [
        item
        for item in read_jsonl(manifest_path)
        if not item.get("relative_path", "").startswith("github-tree/")
    ]
    observed_at = datetime.now(UTC).isoformat()
    accepted = rejected = duplicates = clone_failures = 0
    selection_report: list[dict[str, Any]] = []

    for score, _, repo, commit_count, pr_count in selected:
        source = source_by_url[repo["url"].rstrip("/")]
        with tempfile.TemporaryDirectory(prefix="persona-github-") as temp_dir:
            checkout = Path(temp_dir) / "repo"
            clone = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    "--filter=blob:none",
                    "--quiet",
                    repo["url"],
                    str(checkout),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if clone.returncode != 0:
                clone_failures += 1
                selection_report.append(
                    {"repository": repo["nameWithOwner"], "score": score, "status": "clone_failed"}
                )
                continue
            commit = subprocess.run(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            tracked = subprocess.run(
                ["git", "-C", str(checkout), "ls-files", "-z"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.split("\0")
            candidates: list[Path] = []
            for relative_text in tracked:
                if not relative_text:
                    continue
                relative = Path(relative_text)
                path = checkout / relative
                if (
                    any(part in EXCLUDED_PARTS for part in relative.parts)
                    or relative.name in EXCLUDED_NAMES
                ):
                    continue
                if (
                    path.suffix.lower() not in TEXT_SUFFIXES
                    or not path.is_file()
                    or path.stat().st_size > 1_000_000
                ):
                    continue
                candidates.append(relative)
            candidates.sort(
                key=lambda path: (
                    0 if path.parts[0] in {"src", "app", "lib"} else 1,
                    path.as_posix(),
                )
            )
            seen: set[str] = set()
            repo_accepted = 0
            for relative in candidates[:400]:
                content = (checkout / relative).read_text(encoding="utf-8", errors="replace")
                if not _safe(content):
                    rejected += 1
                    continue
                digest = hashlib.sha256(content.encode()).hexdigest()
                if digest in seen:
                    duplicates += 1
                    continue
                seen.add(digest)
                stored = f"github-tree/{relative.as_posix()}"
                canonical = f"{repo['url']}/blob/{commit}/{quote(relative.as_posix())}"
                documents.append(
                    _record(
                        root,
                        source,
                        stored,
                        content,
                        canonical,
                        observed_at,
                        repo.get("updatedAt"),
                        commit,
                        "github-priority-tree-v1",
                    )
                )
                accepted += 1
                repo_accepted += 1
            selection_report.append(
                {
                    "repository": repo["nameWithOwner"],
                    "score": score,
                    "commits": commit_count,
                    "pull_requests": pr_count,
                    "commit_sha": commit,
                    "tracked_text_documents": repo_accepted,
                    "status": "accepted",
                }
            )

    documents.sort(key=lambda item: (item["source_id"], item["relative_path"]))
    manifest_path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in documents), encoding="utf-8"
    )
    stats: dict[str, Any] = {
        "selected": len(selected),
        "accepted_documents": accepted,
        "rejected": rejected,
        "duplicates": duplicates,
        "clone_failures": clone_failures,
    }
    report = root / "data/research/github-priority-trees.json"
    report.write_text(
        json.dumps(
            {"observed_at": observed_at, **stats, "repositories": selection_report},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return stats
