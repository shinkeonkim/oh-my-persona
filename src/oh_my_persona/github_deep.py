from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .collect import EXCLUDED_NAMES, EXCLUDED_PARTS, TEXT_SUFFIXES
from .corpus import read_jsonl
from .infrastructure.github_support import graphql as _graphql
from .infrastructure.github_support import is_safe as _safe
from .infrastructure.github_support import record_document as _record
from .infrastructure.github_support import rest as _gh

PULL_REQUEST_QUERY = """
query($login:String!, $cursor:String) {
  user(login:$login) {
    pullRequests(first:100, after:$cursor, orderBy:{field:CREATED_AT,direction:DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title body url state createdAt updatedAt closedAt mergedAt
        additions deletions changedFiles commits { totalCount }
        repository { nameWithOwner url }
      }
    }
  }
}
"""


def collect_deep(root: Path, login: str = "shinkeonkim") -> dict[str, int]:
    inventory = json.loads(
        (root / "data/research/github-repositories.json").read_text(encoding="utf-8")
    )
    sources = read_jsonl(root / "data/registry/sources.jsonl")
    by_url = {item["canonical_url"].rstrip("/"): item for item in sources}
    manifest_path = root / "data/registry/documents.jsonl"
    documents = read_jsonl(manifest_path)
    deep_relatives = {"github-readme.md", "github-authored-commits.txt"}
    documents = [item for item in documents if item.get("relative_path") not in deep_relatives]
    observed_at = datetime.now(UTC).isoformat()
    stats = {"repositories": 0, "readmes": 0, "commit_documents": 0, "commits": 0, "rejected": 0}

    for repo in inventory["repositories"]:
        full_name = repo["nameWithOwner"]
        source = by_url[repo["url"].rstrip("/")]
        stats["repositories"] += 1

        readme = _gh(f"repos/{full_name}/readme")
        if readme and readme.get("content"):
            content = base64.b64decode(readme["content"]).decode("utf-8", errors="replace")
            if _safe(content):
                documents.append(
                    _record(
                        root,
                        source,
                        "github-readme.md",
                        content,
                        readme["html_url"],
                        observed_at,
                        repo.get("updatedAt"),
                        readme.get("sha"),
                        "github-readme-v1",
                    )
                )
                stats["readmes"] += 1
            else:
                stats["rejected"] += 1

        pages = (
            _gh(
                f"repos/{full_name}/commits",
                {"author": login, "per_page": "100"},
                paginate=True,
            )
            or []
        )
        commits = [item for page in pages for item in page]
        if commits:
            lines = [f"GitHub repository: {repo['url']}", f"Author account: {login}", ""]
            retained = []
            for item in commits:
                commit = item["commit"]
                authored_at = commit["author"]["date"]
                message = " ".join(commit["message"].split())
                line = f"{authored_at}\t{item['sha']}\t{item['html_url']}\t{message}"
                if _safe(line):
                    lines.append(line)
                    retained.append(item)
                else:
                    stats["rejected"] += 1
            if retained:
                documents.append(
                    _record(
                        root,
                        source,
                        "github-authored-commits.txt",
                        "\n".join(lines) + "\n",
                        f"{repo['url']}/commits?author={login}",
                        observed_at,
                        retained[0]["commit"]["author"]["date"],
                        retained[0]["sha"],
                        "github-authored-commits-v1",
                    )
                )
                stats["commit_documents"] += 1
                stats["commits"] += len(retained)

    documents.sort(key=lambda item: (item["source_id"], item["relative_path"]))
    manifest_path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in documents), encoding="utf-8"
    )
    report = root / "data/research/github-deep-collection.json"
    report.write_text(
        json.dumps({"observed_at": observed_at, **stats}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return stats


def collect_pull_requests(root: Path, login: str = "shinkeonkim") -> dict[str, int]:
    cursor = None
    pull_requests: list[dict[str, Any]] = []
    while True:
        fields = {"login": login}
        if cursor:
            fields["cursor"] = cursor
        connection = _graphql(PULL_REQUEST_QUERY, fields)["user"]["pullRequests"]
        pull_requests.extend(connection["nodes"])
        if not connection["pageInfo"]["hasNextPage"]:
            break
        cursor = connection["pageInfo"]["endCursor"]

    source_by_url = {
        item["canonical_url"].rstrip("/"): item
        for item in read_jsonl(root / "data/registry/sources.jsonl")
    }
    grouped: dict[str, list[dict[str, Any]]] = {}
    skipped = 0
    for item in pull_requests:
        repo_url = item["repository"]["url"].rstrip("/")
        if repo_url not in source_by_url:
            skipped += 1
            continue
        grouped.setdefault(repo_url, []).append(item)

    manifest_path = root / "data/registry/documents.jsonl"
    documents = [
        item
        for item in read_jsonl(manifest_path)
        if item.get("relative_path") != "github-authored-pull-requests.txt"
    ]
    observed_at = datetime.now(UTC).isoformat()
    retained_count = rejected = 0
    for repo_url, items in grouped.items():
        source = source_by_url[repo_url]
        lines = [f"GitHub repository: {repo_url}", f"Pull request author: {login}", ""]
        retained: list[dict[str, Any]] = []
        for item in items:
            body = " ".join((item.get("body") or "").split())[:4000]
            line = (
                f"{item['createdAt']}\t#{item['number']}\t{item['state']}\t{item['url']}\t"
                f"{item['title']}\tmerged={item.get('mergedAt') or ''}\tclosed={item.get('closedAt') or ''}\t"
                f"commits={item['commits']['totalCount']}\tfiles={item['changedFiles']}\t"
                f"+{item['additions']}/-{item['deletions']}\t{body}"
            )
            if _safe(line):
                lines.append(line)
                retained.append(item)
            else:
                rejected += 1
        if retained:
            documents.append(
                _record(
                    root,
                    source,
                    "github-authored-pull-requests.txt",
                    "\n".join(lines) + "\n",
                    f"{repo_url}/pulls?q=is%3Apr+author%3A{login}",
                    observed_at,
                    retained[0]["updatedAt"],
                    None,
                    "github-authored-prs-v1",
                )
            )
            retained_count += len(retained)

    documents.sort(key=lambda item: (item["source_id"], item["relative_path"]))
    manifest_path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in documents), encoding="utf-8"
    )
    stats = {
        "pull_requests": retained_count,
        "repositories": len(grouped),
        "skipped_unregistered": skipped,
        "rejected": rejected,
    }
    report = root / "data/research/github-pull-requests.json"
    report.write_text(
        json.dumps({"observed_at": observed_at, **stats}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return stats


def _doc_paths(tree: list[dict[str, Any]], limit: int = 40) -> list[str]:
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
        paths = _doc_paths(tree_response.get("tree", []))
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
