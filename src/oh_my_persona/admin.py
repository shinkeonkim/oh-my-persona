from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime


class KnowledgeStore:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url
        self._memory: dict[str, dict] = {}
        self._lock = threading.Lock()

    def initialize(self) -> None:
        if not self.database_url:
            return
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_knowledge (
                  id uuid PRIMARY KEY, title text NOT NULL, content text NOT NULL,
                  source_url text NOT NULL CHECK (source_url LIKE 'https://%'),
                  observed_at date, status text NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','draft')),
                  created_at timestamptz NOT NULL DEFAULT now(),
                  updated_at timestamptz NOT NULL DEFAULT now()
                )
            """)

    def list(self, limit: int = 100, offset: int = 0) -> list[dict]:
        if not self.database_url:
            return list(self._memory.values())[offset : offset + limit]
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            rows = connection.execute(
                "SELECT * FROM admin_knowledge ORDER BY updated_at DESC LIMIT %s OFFSET %s",
                (limit, offset),
            ).fetchall()
        return [_serialize(row) for row in rows]

    def active(self) -> list[dict]:
        return [item for item in self.list(limit=5000) if item["status"] == "active"]

    def get(self, item_id: str) -> dict | None:
        try:
            uuid.UUID(item_id)
        except ValueError:
            return None
        if not self.database_url:
            return self._memory.get(item_id)
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            row = connection.execute(
                "SELECT * FROM admin_knowledge WHERE id=%s", (item_id,)
            ).fetchone()
        return _serialize(row) if row else None

    def create(self, values: dict) -> dict:
        item_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        item = {"id": item_id, **values, "created_at": now, "updated_at": now}
        if not self.database_url:
            with self._lock:
                self._memory[item_id] = item
            return item
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """INSERT INTO admin_knowledge(id,title,content,source_url,observed_at,status)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (item_id, values["title"], values["content"], values["source_url"],
                 values.get("observed_at"), values["status"]),
            )
        return self.get(item_id) or item

    def update(self, item_id: str, values: dict) -> dict | None:
        if not self.get(item_id):
            return None
        if not self.database_url:
            with self._lock:
                current = self._memory[item_id]
                current.update(values)
                current["updated_at"] = datetime.now(UTC).isoformat()
                return dict(current)
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """UPDATE admin_knowledge SET title=%s,content=%s,source_url=%s,
                   observed_at=%s,status=%s,updated_at=now() WHERE id=%s""",
                (values["title"], values["content"], values["source_url"],
                 values.get("observed_at"), values["status"], item_id),
            )
        return self.get(item_id)

    def delete(self, item_id: str) -> bool:
        if not self.database_url:
            with self._lock:
                return self._memory.pop(item_id, None) is not None
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            result = connection.execute("DELETE FROM admin_knowledge WHERE id=%s", (item_id,))
            return result.rowcount > 0


def _serialize(row: dict) -> dict:
    return {key: value.isoformat() if hasattr(value, "isoformat") else value for key, value in row.items()}
