from __future__ import annotations

import builtins
import uuid
from datetime import UTC, datetime
from typing import Any


class PostgresKnowledgeStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def initialize(self) -> None:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS admin_knowledge (
                  id uuid PRIMARY KEY, title text NOT NULL, content text NOT NULL,
                  source_url text NOT NULL CHECK (source_url LIKE 'https://%'),
                  observed_at date, status text NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','draft')),
                  created_at timestamptz NOT NULL DEFAULT now(),
                  updated_at timestamptz NOT NULL DEFAULT now())
            """)

    def list(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            rows = connection.execute(
                "SELECT * FROM admin_knowledge ORDER BY updated_at DESC LIMIT %s OFFSET %s",
                (limit, offset),
            ).fetchall()
        return [_serialize(row) for row in rows]

    def active(self) -> builtins.list[dict[str, Any]]:
        return [item for item in self.list(limit=5000) if item["status"] == "active"]

    def get(self, item_id: str) -> dict[str, Any] | None:
        import psycopg
        from psycopg.rows import dict_row

        if not _valid_uuid(item_id):
            return None
        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            row = connection.execute(
                "SELECT * FROM admin_knowledge WHERE id=%s", (item_id,)
            ).fetchone()
        return _serialize(row) if row else None

    def create(self, values: dict[str, Any]) -> dict[str, Any]:
        import psycopg

        item_id = str(uuid.uuid4())
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """INSERT INTO admin_knowledge(id,title,content,source_url,observed_at,status)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (
                    item_id,
                    values["title"],
                    values["content"],
                    values["source_url"],
                    values.get("observed_at"),
                    values["status"],
                ),
            )
        return self.get(item_id) or _fallback_item(item_id, values)

    def update(self, item_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        import psycopg

        if not self.get(item_id):
            return None
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """UPDATE admin_knowledge SET title=%s,content=%s,source_url=%s,
                   observed_at=%s,status=%s,updated_at=now() WHERE id=%s""",
                (
                    values["title"],
                    values["content"],
                    values["source_url"],
                    values.get("observed_at"),
                    values["status"],
                    item_id,
                ),
            )
        return self.get(item_id)

    def delete(self, item_id: str) -> bool:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            result = connection.execute("DELETE FROM admin_knowledge WHERE id=%s", (item_id,))
        return result.rowcount > 0


class PostgresKnowledgeQuestionStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def initialize(self) -> None:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS admin_knowledge_questions (
                  id uuid PRIMARY KEY, question text NOT NULL, category text NOT NULL,
                  time_scope text NOT NULL, created_at timestamptz NOT NULL DEFAULT now())
            """)

    def list(self) -> list[dict[str, Any]]:
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            rows = connection.execute(
                "SELECT * FROM admin_knowledge_questions ORDER BY created_at DESC"
            ).fetchall()
        return [_question_item(row) for row in rows]

    def get(self, question_id: str) -> dict[str, Any] | None:
        import psycopg
        from psycopg.rows import dict_row

        raw_id = question_id.removeprefix("AQ-")
        if not _valid_uuid(raw_id):
            return None
        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            row = connection.execute(
                "SELECT * FROM admin_knowledge_questions WHERE id=%s", (raw_id,)
            ).fetchone()
        return _question_item(row) if row else None

    def create(self, values: dict[str, Any]) -> dict[str, Any]:
        import psycopg

        raw_id = str(uuid.uuid4())
        question_id = f"AQ-{raw_id}"
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """INSERT INTO admin_knowledge_questions(id,question,category,time_scope)
                   VALUES (%s,%s,%s,%s)""",
                (raw_id, values["question"], values["category"], values["time_scope"]),
            )
        return self.get(question_id) or {
            "question_id": question_id,
            **values,
            "created_at": datetime.now(UTC).isoformat(),
        }

    def delete(self, question_id: str) -> bool:
        import psycopg

        raw_id = question_id.removeprefix("AQ-")
        if not _valid_uuid(raw_id):
            return False
        with psycopg.connect(self.database_url) as connection:
            result = connection.execute(
                "DELETE FROM admin_knowledge_questions WHERE id=%s", (raw_id,)
            )
        return result.rowcount > 0


def _question_item(row: dict[str, Any]) -> dict[str, Any]:
    item = _serialize(row)
    item["question_id"] = f"AQ-{item.pop('id')}"
    return item


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value.isoformat() if hasattr(value, "isoformat") else value
        for key, value in row.items()
    }


def _fallback_item(item_id: str, values: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(UTC).isoformat()
    return {"id": item_id, **values, "created_at": now, "updated_at": now}


def _valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except ValueError:
        return False
    return True
