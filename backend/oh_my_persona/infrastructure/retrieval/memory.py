from __future__ import annotations

import math
from collections import Counter
from dataclasses import replace
from itertools import pairwise
from pathlib import Path

from ...domain.chunks import chunk_text
from ...domain.search import SearchHit, tokenize
from ..files import read_jsonl

QUERY_EXPANSIONS = {
    "미핏": ("mefit", "kmu-aws-capstone-team-4"),
    "mefit": ("미핏", "kmu-aws-capstone-team-4"),
}


class MemoryRetriever:
    def __init__(self, root: Path) -> None:
        self.root = root
        sources = read_jsonl(root / "data/registry/sources.jsonl")
        self.sources = {item["source_id"]: item for item in sources}
        self.records: list[tuple[SearchHit, Counter[str]]] = []
        self._load_claims(root)
        self._load_chunks(root)

    def _load_claims(self, root: Path) -> None:
        for claim in read_jsonl(root / "data/curated/claims.jsonl"):
            valid_at = claim.get("valid_at")
            date_text = (
                " ".join(str(value) for value in valid_at.values())
                if isinstance(valid_at, dict)
                else str(valid_at or "")
            )
            text = f"{claim['subject']} {claim['predicate']} {claim['object']} {date_text}".strip()
            for source_id in claim["source_ids"]:
                source = self.sources.get(source_id, {})
                hit = SearchHit(
                    chunk_id=f"{claim['claim_id']}:{source_id}",
                    text=text,
                    score=0.0,
                    source_id=source.get("source_id"),
                    title=source.get("title"),
                    url=source.get("canonical_url"),
                    published_at=source.get("published_at"),
                    observed_at=source.get("observed_at"),
                    metadata={
                        "claim_id": claim["claim_id"],
                        "kind": claim.get("kind"),
                        "valid_at": claim.get("valid_at"),
                    },
                )
                self.records.append((hit, Counter(tokenize(text))))

    def _load_chunks(self, root: Path) -> None:
        processed = read_jsonl(root / "data/processed/chunks.jsonl")
        if not processed:
            self._load_authored_files(root)
            return
        for chunk in processed:
            source = self.sources.get(chunk.get("source_id"), {})
            hit = SearchHit(
                chunk["chunk_id"],
                chunk["text"],
                0.0,
                chunk.get("source_id"),
                source.get("title"),
                chunk.get("canonical_url") or source.get("canonical_url"),
                source.get("published_at"),
                chunk.get("observed_at") or source.get("observed_at"),
                {"source_path": chunk["source_path"], "document_id": chunk.get("document_id")},
            )
            self.records.append((hit, Counter(tokenize(chunk["text"]))))

    def _load_authored_files(self, root: Path) -> None:
        for directory in (root / "data" / "raw", root / "data" / "curated", root / "docs"):
            if not directory.exists():
                continue
            paths = sorted(path for path in directory.rglob("*") if path.suffix in {".md", ".txt"})
            for path in paths:
                relative = str(path.relative_to(root))
                for chunk in chunk_text(path.read_text(encoding="utf-8"), relative):
                    hit = SearchHit(
                        chunk.chunk_id,
                        chunk.text,
                        0.0,
                        metadata={"source_path": chunk.source_path},
                    )
                    self.records.append((hit, Counter(tokenize(chunk.text))))

    def search(self, query: str, limit: int = 6) -> list[SearchHit]:
        terms = self._expanded_terms(query)
        if not terms:
            return []
        query_tokens = tokenize(query)
        document_count = max(len(self.records), 1)
        document_frequency = Counter(term for _, tokens in self.records for term in tokens)
        scored = [
            scored_hit
            for hit, tokens in self.records
            if (
                scored_hit := self._score(
                    hit, tokens, terms, query_tokens, document_count, document_frequency
                )
            )
        ]
        ranked = sorted(
            scored, key=lambda item: (item.source_id is None, -item.score, item.chunk_id)
        )
        return self._diversify(ranked, limit)

    def _expanded_terms(self, query: str) -> Counter[str]:
        expansions = [
            term
            for alias, terms in QUERY_EXPANSIONS.items()
            if alias in query.lower()
            for term in terms
        ]
        return Counter(tokenize(" ".join((query, *expansions))))

    def _score(
        self,
        hit: SearchHit,
        tokens: Counter[str],
        terms: Counter[str],
        query_tokens: list[str],
        document_count: int,
        frequencies: Counter[str],
    ) -> SearchHit | None:
        score = sum(
            (1 + math.log(tokens[term]))
            * (math.log((document_count + 1) / (frequencies[term] + 1)) + 1)
            * count
            for term, count in terms.items()
            if tokens[term]
        )
        if not score:
            return None
        adjacent = sum(
            1 for left, right in pairwise(query_tokens) if f"{left} {right}" in hit.text.lower()
        )
        score *= 1 + min(adjacent, 4) * 0.2
        source = self.sources.get(hit.source_id or "", {})
        if hit.metadata.get("claim_id"):
            score *= 2.0
        elif source.get("source_type") == "first_person_interview":
            score *= 1.9
        elif hit.source_id in {"SRC-0001", "SRC-0002"}:
            score *= 1.7
        elif source.get("source_type") in {"blog_post", "about_page", "website"}:
            score *= 1.35
        elif hit.source_id in {"SRC-0011", "SRC-0013"}:
            score *= 1.2
        elif hit.source_id == "SRC-0012":
            score *= 1.45
        return replace(hit, score=round(score, 6))

    @staticmethod
    def _diversify(ranked: list[SearchHit], limit: int) -> list[SearchHit]:
        output: list[SearchHit] = []
        seen_claims: set[str] = set()
        for hit in ranked:
            claim_id = hit.metadata.get("claim_id")
            if claim_id and claim_id in seen_claims:
                continue
            output.append(hit)
            if claim_id:
                seen_claims.add(claim_id)
            if len(output) == limit:
                break
        return output
