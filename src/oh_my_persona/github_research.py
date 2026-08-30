from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .corpus import read_jsonl

QUERY = """
query($login:String!, $ownedCursor:String, $contributedCursor:String) {
  user(login:$login) {
    organizations(first:100) { nodes { login url } }
    repositories(first:100, after:$ownedCursor, ownerAffiliations:OWNER, privacy:PUBLIC,
      orderBy:{field:NAME,direction:ASC}) {
      pageInfo { hasNextPage endCursor }
      nodes { ...RepoFields }
    }
    repositoriesContributedTo(first:100, after:$contributedCursor, includeUserRepositories:false,
      contributionTypes:[COMMIT,ISSUE,PULL_REQUEST,REPOSITORY]) {
      pageInfo { hasNextPage endCursor }
      nodes { ...RepoFields }
    }
  }
}
fragment RepoFields on Repository {
  nameWithOwner url description isFork isArchived createdAt updatedAt pushedAt
  owner { login }
  primaryLanguage { name }
  languages(first:10, orderBy:{field:SIZE,direction:DESC}) { nodes { name } }
  repositoryTopics(first:20) { nodes { topic { name } } }
  defaultBranchRef { name target { ... on Commit { oid committedDate } } }
}
"""


def _graphql(login: str, owned_cursor: str | None, contributed_cursor: str | None) -> dict[str, Any]:
    command = ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={login}"]
    if owned_cursor:
        command.extend(("-F", f"ownedCursor={owned_cursor}"))
    if contributed_cursor:
        command.extend(("-F", f"contributedCursor={contributed_cursor}"))
    for attempt in range(3):
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)["data"]["user"]
        if attempt < 2:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"GitHub GraphQL request failed: {result.stderr.strip()}")


def discover(login: str = "shinkeonkim") -> dict[str, Any]:
    repos: dict[str, dict[str, Any]] = {}
    organizations: dict[str, str] = {}
    owned_cursor = contributed_cursor = None
    owned_done = contributed_done = False
    while not (owned_done and contributed_done):
        user = _graphql(login, owned_cursor, contributed_cursor)
        organizations.update({item["login"]: item["url"] for item in user["organizations"]["nodes"]})
        for relation, connection in (
            ("owner", user["repositories"]),
            ("contributor", user["repositoriesContributedTo"]),
        ):
            for repo in connection["nodes"]:
                item = repos.setdefault(repo["nameWithOwner"], repo | {"relations": []})
                if relation not in item["relations"]:
                    item["relations"].append(relation)
        owned_done = not user["repositories"]["pageInfo"]["hasNextPage"]
        contributed_done = not user["repositoriesContributedTo"]["pageInfo"]["hasNextPage"]
        owned_cursor = user["repositories"]["pageInfo"]["endCursor"] if not owned_done else owned_cursor
        contributed_cursor = user["repositoriesContributedTo"]["pageInfo"]["endCursor"] if not contributed_done else contributed_cursor
    return {
        "login": login,
        "observed_at": datetime.now(UTC).isoformat(),
        "organizations": [{"login": key, "url": organizations[key]} for key in sorted(organizations)],
        "repositories": [repos[key] for key in sorted(repos)],
    }


def write_inventory(root: Path, inventory: dict[str, Any]) -> dict[str, int]:
    output = root / "data/research/github-repositories.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    source_path = root / "data/registry/sources.jsonl"
    document_path = root / "data/registry/documents.jsonl"
    sources = read_jsonl(source_path)
    documents = read_jsonl(document_path)
    by_url = {item["canonical_url"].rstrip("/"): item for item in sources}
    next_id = max(int(item["source_id"].split("-")[1]) for item in sources) + 1
    observed_at = inventory["observed_at"]
    added_sources = 0

    for repo in inventory["repositories"]:
        url = repo["url"].rstrip("/")
        if url not in by_url:
            source = {
                "source_id": f"SRC-{next_id:04d}", "canonical_url": url,
                "source_type": "repository", "title": repo["nameWithOwner"],
                "publisher": repo["owner"]["login"], "observed_at": observed_at,
                "identity_signals": [inventory["login"], *repo["relations"]],
                "collection": "github_graphql", "trust": "public_contribution",
                "status": "accepted",
            }
            sources.append(source)
            by_url[url] = source
            next_id += 1
            added_sources += 1

        source = by_url[url]
        branch = repo.get("defaultBranchRef") or {}
        target = branch.get("target") or {}
        content = "\n".join((
            f"GitHub repository: {repo['nameWithOwner']}",
            f"URL: {url}",
            f"Relationship to shinkeonkim: {', '.join(repo['relations'])}",
            f"Description: {repo.get('description') or '(none)'}",
            f"Created at: {repo.get('createdAt')}", f"Updated at: {repo.get('updatedAt')}",
            f"Pushed at: {repo.get('pushedAt')}", f"Archived: {repo.get('isArchived')}",
            f"Fork: {repo.get('isFork')}",
            f"Languages: {', '.join(node['name'] for node in repo['languages']['nodes']) or '(none)'}",
            f"Topics: {', '.join(node['topic']['name'] for node in repo['repositoryTopics']['nodes']) or '(none)'}",
            f"Default branch: {branch.get('name') or '(none)'}",
            f"Latest commit: {target.get('oid') or '(none)'} at {target.get('committedDate') or '(none)'}",
        )) + "\n"
        digest = hashlib.sha256(content.encode()).hexdigest()
        raw = root / "data/raw" / source["source_id"] / "github-metadata.txt"
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_text(content, encoding="utf-8")
        documents = [item for item in documents if not (
            item.get("source_id") == source["source_id"] and item.get("relative_path") == "github-metadata.txt"
        )]
        documents.append({
            "document_id": f"DOC-{digest[:20]}", "source_id": source["source_id"],
            "canonical_url": url, "repository_url": url,
            "commit_sha": target.get("oid"), "relative_path": "github-metadata.txt",
            "raw_path": str(raw.relative_to(root)), "content_sha256": digest,
            "mime_type": "text/plain", "published_at": repo.get("updatedAt"),
            "observed_at": observed_at, "extractor_version": "github-graphql-v1",
            "status": "accepted",
        })

    sources.sort(key=lambda item: item["source_id"])
    documents.sort(key=lambda item: (item["source_id"], item["relative_path"]))
    source_path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in sources), encoding="utf-8")
    document_path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in documents), encoding="utf-8")
    return {"organizations": len(inventory["organizations"]), "repositories": len(inventory["repositories"]), "added_sources": added_sources}
