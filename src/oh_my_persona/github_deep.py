"""Backward-compatible façade for GitHub collection commands."""

from .infrastructure.github_activity import collect_deep, collect_pull_requests
from .infrastructure.github_documents import _doc_paths, collect_public_docs
from .infrastructure.github_trees import collect_priority_trees

__all__ = [
    "_doc_paths",
    "collect_deep",
    "collect_priority_trees",
    "collect_public_docs",
    "collect_pull_requests",
]
