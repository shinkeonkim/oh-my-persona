from __future__ import annotations

import base64
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..corpus import read_jsonl
from .github_support import graphql as _graphql
from .github_support import is_safe as _safe
from .github_support import record_document as _record
from .github_support import rest as _gh

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
