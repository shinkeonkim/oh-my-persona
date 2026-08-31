"""Backward-compatible façade for GitHub collection commands."""

from .activity import collect_deep, collect_pull_requests
from .documents import _doc_paths, collect_public_docs
from .trees import collect_priority_trees

__all__ = [
    "_doc_paths",
    "collect_deep",
    "collect_priority_trees",
    "collect_public_docs",
    "collect_pull_requests",
]
