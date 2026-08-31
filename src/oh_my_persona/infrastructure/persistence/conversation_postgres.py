from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any


class PostgresConversationStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def initialize(self) -> None:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                  id uuid PRIMARY KEY, created_at timestamptz NOT NULL DEFAULT now(),
                  updated_at timestamptz NOT NULL DEFAULT now(), metadata jsonb NOT NULL DEFAULT '{}');
                CREATE TABLE IF NOT EXISTS conversation_messages (
                  id bigserial PRIMARY KEY, conversation_id uuid NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                  role text NOT NULL CHECK (role IN ('user','assistant','owner')), content text NOT NULL,
                  model text, sources jsonb NOT NULL DEFAULT '[]', created_at timestamptz NOT NULL DEFAULT now());
                CREATE INDEX IF NOT EXISTS conversation_messages_order_idx
                  ON conversation_messages(conversation_id, id);
                CREATE TABLE IF NOT EXISTS rate_limit_events (
                  id bigserial PRIMARY KEY, identity_hash char(64) NOT NULL,
                  created_at timestamptz NOT NULL DEFAULT now());
                CREATE INDEX IF NOT EXISTS rate_limit_events_lookup_idx
                  ON rate_limit_events(identity_hash, created_at);
                ALTER TABLE conversation_messages DROP CONSTRAINT IF EXISTS conversation_messages_role_check;
                ALTER TABLE conversation_messages ADD CONSTRAINT conversation_messages_role_check
                  CHECK (role IN ('user','assistant','owner'));
            """)

    def create(self, metadata: dict[str, Any] | None = None) -> str:
        import psycopg

        conversation_id = str(uuid.uuid4())
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                "INSERT INTO conversations(id,metadata) VALUES (%s,%s::jsonb)",
                (conversation_id, json.dumps(metadata or {})),
            )
        return conversation_id

    def metadata(self, conversation_id: str) -> dict[str, Any]:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT metadata FROM conversations WHERE id=%s", (conversation_id,)
            ).fetchone()
        return dict(row[0]) if row else {}

    def update_metadata(self, conversation_id: str, values: dict[str, Any]) -> None:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                "UPDATE conversations SET metadata=metadata || %s::jsonb WHERE id=%s",
                (json.dumps(values), conversation_id),
            )

    def conversation_for_discord_thread(self, thread_id: str, active_days: int = 30) -> str | None:
        import psycopg

        cutoff = datetime.now(UTC) - timedelta(days=active_days)
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                """SELECT id FROM conversations WHERE metadata->>'discord_thread_id'=%s
                   AND updated_at >= %s ORDER BY updated_at DESC LIMIT 1""",
                (thread_id, cutoff),
            ).fetchone()
        return str(row[0]) if row else None

    def exists(self, conversation_id: str) -> bool:
        import psycopg

        try:
            uuid.UUID(conversation_id)
        except ValueError:
            return False
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT 1 FROM conversations WHERE id=%s", (conversation_id,)
            ).fetchone()
        return row is not None

    def messages(self, conversation_id: str, limit: int = 40) -> list[dict[str, Any]]:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            rows = list(
                reversed(
                    connection.execute(
                        """SELECT role,content,model,sources,created_at FROM conversation_messages
                   WHERE conversation_id=%s ORDER BY id DESC LIMIT %s""",
                        (conversation_id, limit),
                    ).fetchall()
                )
            )
        return [
            {
                "role": row[0],
                "content": row[1],
                "model": row[2],
                "sources": row[3],
                "created_at": row[4].isoformat(),
            }
            for row in rows
        ]

    def append(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model: str | None = None,
        sources: list[dict[str, Any]] | None = None,
    ) -> None:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """INSERT INTO conversation_messages(conversation_id,role,content,model,sources)
                   VALUES (%s,%s,%s,%s,%s::jsonb)""",
                (
                    conversation_id,
                    role,
                    content,
                    model,
                    json.dumps(sources or [], ensure_ascii=False),
                ),
            )
            connection.execute(
                "UPDATE conversations SET updated_at=now() WHERE id=%s", (conversation_id,)
            )

    def list_conversations(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            rows = connection.execute(
                """SELECT c.id,c.created_at,c.updated_at,count(m.id)::integer AS message_count,
                   coalesce((array_agg(m.content ORDER BY m.id) FILTER (WHERE m.role='user'))[1],'') AS preview
                   FROM conversations c LEFT JOIN conversation_messages m ON m.conversation_id=c.id
                   GROUP BY c.id HAVING count(m.id) > 0 ORDER BY c.updated_at DESC LIMIT %s OFFSET %s""",
                (limit, offset),
            ).fetchall()
        return [
            {
                key: value.isoformat() if hasattr(value, "isoformat") else value
                for key, value in row.items()
            }
            for row in rows
        ]
