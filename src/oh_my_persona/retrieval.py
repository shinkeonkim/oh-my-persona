from __future__ import annotations

import math
import re
from collections import Counter
from itertools import pairwise
from pathlib import Path
from typing import Protocol

from .corpus import chunk_text, iter_corpus_files, read_jsonl
from .models import SearchHit

TOKEN = re.compile(r"[0-9A-Za-z가-힣][0-9A-Za-z가-힣_.+#-]*")
KOREAN_SUFFIXES = ("에서는", "으로부터", "에게서", "까지", "부터", "에서", "으로", "에게", "께서", "처럼", "보다", "은", "는", "이", "가", "을", "를", "의", "에", "와", "과", "도", "로")


class Retriever(Protocol):
    def search(self, query: str, limit: int = 6) -> list[SearchHit]: ...


def tokenize(text: str) -> list[str]:
    output: list[str] = []
    for raw in TOKEN.findall(text):
        token = raw.lower()
        output.append(token)
        if any("가" <= character <= "힣" for character in token) and len(token) >= 3:
            output.extend(token[index : index + 3] for index in range(len(token) - 2))
        for suffix in KOREAN_SUFFIXES:
            if token.endswith(suffix) and len(token) > len(suffix) + 1:
                output.append(token[: -len(suffix)])
                break
    return output


class MemoryRetriever:
    def __init__(self, root: Path):
        self.root = root
        sources = read_jsonl(root / "data/registry/sources.jsonl")
        self.sources = {item["source_id"]: item for item in sources}
        claims = read_jsonl(root / "data/curated/claims.jsonl")
        self.records: list[tuple[SearchHit, Counter[str]]] = []
        for claim in claims:
            valid_at = claim.get("valid_at")
            date_text = " ".join(str(value) for value in valid_at.values()) if isinstance(valid_at, dict) else str(valid_at or "")
            text = f"{claim['subject']} {claim['predicate']} {claim['object']} {date_text}".strip()
            for source_id in claim["source_ids"]:
                source = self.sources.get(source_id, {})
                hit = SearchHit(
                    chunk_id=f"{claim['claim_id']}:{source_id}", text=text, score=0.0,
                    source_id=source.get("source_id"), title=source.get("title"),
                    url=source.get("canonical_url"), published_at=source.get("published_at"),
                    observed_at=source.get("observed_at"),
                    metadata={"claim_id": claim["claim_id"], "kind": claim.get("kind"), "valid_at": claim.get("valid_at")},
                )
                self.records.append((hit, Counter(tokenize(text))))
        processed = read_jsonl(root / "data/processed/chunks.jsonl")
        if processed:
            for chunk in processed:
                source = self.sources.get(chunk.get("source_id"), {})
                hit = SearchHit(
                    chunk["chunk_id"], chunk["text"], 0.0, chunk.get("source_id"),
                    source.get("title"), chunk.get("canonical_url") or source.get("canonical_url"),
                    source.get("published_at"), chunk.get("observed_at") or source.get("observed_at"),
                    {"source_path": chunk["source_path"], "document_id": chunk.get("document_id")},
                )
                self.records.append((hit, Counter(tokenize(chunk["text"]))))
        else:
            for path in iter_corpus_files(root):
                for chunk in chunk_text(path.read_text(encoding="utf-8"), str(path.relative_to(root))):
                    hit = SearchHit(chunk.chunk_id, chunk.text, 0.0, metadata={"source_path": chunk.source_path})
                    self.records.append((hit, Counter(tokenize(chunk.text))))

    def search(self, query: str, limit: int = 6) -> list[SearchHit]:
        terms = Counter(tokenize(query))
        query_tokens = tokenize(query)
        if not terms:
            return []
        scored: list[SearchHit] = []
        document_count = max(len(self.records), 1)
        document_frequency = Counter(term for _, tokens in self.records for term in tokens)
        for hit, tokens in self.records:
            score = 0.0
            for term, query_count in terms.items():
                if tokens[term]:
                    inverse = math.log((document_count + 1) / (document_frequency[term] + 1)) + 1
                    score += (1 + math.log(tokens[term])) * inverse * query_count
            if score:
                lowered_text = hit.text.lower()
                adjacent_matches = sum(
                    1 for left, right in pairwise(query_tokens)
                    if f"{left} {right}" in lowered_text
                )
                score *= 1 + min(adjacent_matches, 4) * 0.2
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
                scored.append(SearchHit(**{**hit.__dict__, "score": round(score, 6)}))
        # Public citations are preferred over uncited narrative chunks at equal relevance.
        # Narrative chunks remain useful context but cannot alone support a public answer.
        ranked = sorted(scored, key=lambda item: (item.source_id is None, -item.score, item.chunk_id))
        diversified: list[SearchHit] = []
        seen_claims: set[str] = set()
        for hit in ranked:
            claim_id = hit.metadata.get("claim_id")
            if claim_id and claim_id in seen_claims:
                continue
            diversified.append(hit)
            if claim_id:
                seen_claims.add(claim_id)
            if len(diversified) == limit:
                break
        return diversified


class PostgresHybridRetriever:
    def __init__(self, database_url: str, embedding):
        self.database_url = database_url
        self.embedding = embedding

    def search(self, query: str, limit: int = 6) -> list[SearchHit]:
        import psycopg
        vector = self.embedding(query)
        sql = """
        WITH lexical AS (
          SELECT c.id, row_number() OVER (ORDER BY ts_rank_cd(c.search_vector, websearch_to_tsquery('simple', %(q)s)) DESC) rank
          FROM chunks c WHERE c.search_vector @@ websearch_to_tsquery('simple', %(q)s) LIMIT 30
        ), semantic AS (
          SELECT c.id, row_number() OVER (ORDER BY e.embedding <=> %(v)s::vector) rank
          FROM embeddings e JOIN chunks c ON c.id=e.chunk_id WHERE e.model=%(m)s LIMIT 30
        ), fused AS (
          SELECT coalesce(l.id,s.id) id, coalesce(1.0/(60+l.rank),0)+coalesce(1.0/(60+s.rank),0) score
          FROM lexical l FULL JOIN semantic s ON l.id=s.id
        )
        SELECT c.id,c.content,f.score,s.id,s.title,s.canonical_url,s.published_at,s.observed_at
        FROM fused f JOIN chunks c ON c.id=f.id JOIN documents d ON d.id=c.document_id JOIN sources s ON s.id=d.source_id
        ORDER BY f.score DESC LIMIT %(limit)s
        """
        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute(sql, {"q": query, "v": vector.values, "m": vector.model, "limit": limit})
            return [SearchHit(str(row[0]), row[1], float(row[2]), str(row[3]), row[4], row[5], _iso(row[6]), _iso(row[7])) for row in cursor.fetchall()]


def _iso(value):
    return value.isoformat() if value else None
