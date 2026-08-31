from __future__ import annotations

from typing import Any

from ...domain.search import SearchHit


class PostgresHybridRetriever:
    def __init__(self, database_url: str, embedding: Any) -> None:
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
        with psycopg.connect(self.database_url) as connection:
            rows = connection.execute(
                sql,
                {"q": query, "v": vector.values, "m": vector.model, "limit": limit},
            ).fetchall()
        return [
            SearchHit(
                str(row[0]),
                row[1],
                float(row[2]),
                str(row[3]),
                row[4],
                row[5],
                _iso(row[6]),
                _iso(row[7]),
            )
            for row in rows
        ]


def _iso(value: Any) -> str | None:
    return value.isoformat() if value else None
