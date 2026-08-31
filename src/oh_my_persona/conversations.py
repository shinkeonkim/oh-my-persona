from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import UTC, datetime, timedelta


class ConversationStore:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.environ.get("PERSONA_DATABASE_URL")
        self._lock = threading.Lock()
        self._memory: dict[str, list[dict]] = {}
        self._metadata: dict[str, dict] = {}

    def initialize(self) -> None:
        if not self.database_url:
            return
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                  id uuid PRIMARY KEY, created_at timestamptz NOT NULL DEFAULT now(),
                  updated_at timestamptz NOT NULL DEFAULT now(), metadata jsonb NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS conversation_messages (
                  id bigserial PRIMARY KEY, conversation_id uuid NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                  role text NOT NULL CHECK (role IN ('user','assistant','owner')), content text NOT NULL,
                  model text, sources jsonb NOT NULL DEFAULT '[]', created_at timestamptz NOT NULL DEFAULT now()
                );
                CREATE INDEX IF NOT EXISTS conversation_messages_order_idx
                  ON conversation_messages(conversation_id, id);
                CREATE TABLE IF NOT EXISTS rate_limit_events (
                  id bigserial PRIMARY KEY, identity_hash char(64) NOT NULL,
                  created_at timestamptz NOT NULL DEFAULT now()
                );
                CREATE INDEX IF NOT EXISTS rate_limit_events_lookup_idx
                  ON rate_limit_events(identity_hash, created_at);
                ALTER TABLE conversation_messages DROP CONSTRAINT IF EXISTS conversation_messages_role_check;
                ALTER TABLE conversation_messages ADD CONSTRAINT conversation_messages_role_check
                  CHECK (role IN ('user','assistant','owner'));
            """)

    def create(self, metadata: dict | None = None) -> str:
        conversation_id = str(uuid.uuid4())
        if not self.database_url:
            with self._lock:
                self._memory[conversation_id] = []
                self._metadata[conversation_id] = metadata or {}
            return conversation_id
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO conversations(id,metadata) VALUES (%s,%s::jsonb)",
                (conversation_id, json.dumps(metadata or {})),
            )
        return conversation_id

    def metadata(self, conversation_id: str) -> dict:
        if not self.database_url:
            return dict(self._metadata.get(conversation_id, {}))
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute("SELECT metadata FROM conversations WHERE id=%s", (conversation_id,))
            row = cursor.fetchone()
        return dict(row[0]) if row else {}

    def update_metadata(self, conversation_id: str, values: dict) -> None:
        if not self.database_url:
            with self._lock:
                current = self._metadata.setdefault(conversation_id, {})
                current.update(values)
            return
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE conversations SET metadata=metadata || %s::jsonb WHERE id=%s",
                (json.dumps(values), conversation_id),
            )

    def conversation_for_discord_thread(self, thread_id: str, active_days: int = 30) -> str | None:
        cutoff = datetime.now(UTC) - timedelta(days=active_days)
        if not self.database_url:
            for conversation_id, metadata in self._metadata.items():
                if metadata.get("discord_thread_id") != thread_id:
                    continue
                messages = self._memory.get(conversation_id, [])
                last_at = messages[-1]["created_at"] if messages else metadata.get("created_at")
                if last_at and datetime.fromisoformat(last_at) >= cutoff:
                    return conversation_id
            return None
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute(
                """SELECT id FROM conversations
                   WHERE metadata->>'discord_thread_id'=%s AND updated_at >= %s
                   ORDER BY updated_at DESC LIMIT 1""",
                (thread_id, cutoff),
            )
            row = cursor.fetchone()
        return str(row[0]) if row else None

    def exists(self, conversation_id: str) -> bool:
        try:
            uuid.UUID(conversation_id)
        except ValueError:
            return False
        if not self.database_url:
            return conversation_id in self._memory
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM conversations WHERE id=%s", (conversation_id,))
            return cursor.fetchone() is not None

    def messages(self, conversation_id: str, limit: int = 40) -> list[dict]:
        if not self.database_url:
            return list(self._memory.get(conversation_id, []))[-limit:]
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute(
                """SELECT role,content,model,sources,created_at FROM conversation_messages
                   WHERE conversation_id=%s ORDER BY id DESC LIMIT %s""",
                (conversation_id, limit),
            )
            rows = list(reversed(cursor.fetchall()))
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
        sources: list[dict] | None = None,
    ) -> None:
        created_at = datetime.now(UTC).isoformat()
        item = {
            "role": role,
            "content": content,
            "model": model,
            "sources": sources or [],
            "created_at": created_at,
        }
        if not self.database_url:
            with self._lock:
                self._memory.setdefault(conversation_id, []).append(item)
            return
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute(
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
            cursor.execute(
                "UPDATE conversations SET updated_at=now() WHERE id=%s", (conversation_id,)
            )

    def list_conversations(self, limit: int = 100, offset: int = 0) -> list[dict]:
        if not self.database_url:
            items = []
            for conversation_id, messages in reversed(list(self._memory.items())):
                if not messages:
                    continue
                items.append(
                    {
                        "id": conversation_id,
                        "message_count": len(messages),
                        "preview": messages[0]["content"][:160] if messages else "",
                        "updated_at": messages[-1]["created_at"] if messages else None,
                    }
                )
            return items[offset : offset + limit]
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            rows = connection.execute(
                """SELECT c.id,c.created_at,c.updated_at,count(m.id)::integer AS message_count,
                   coalesce((array_agg(m.content ORDER BY m.id)
                     FILTER (WHERE m.role='user'))[1],'') AS preview
                   FROM conversations c LEFT JOIN conversation_messages m ON m.conversation_id=c.id
                   GROUP BY c.id HAVING count(m.id) > 0
                   ORDER BY c.updated_at DESC LIMIT %s OFFSET %s""",
                (limit, offset),
            ).fetchall()
        return [
            {
                key: value.isoformat() if hasattr(value, "isoformat") else value
                for key, value in row.items()
            }
            for row in rows
        ]


# Compatibility export; new code should import the infrastructure adapter directly.
from .infrastructure.rate_limit import RateLimiter

__all__ = ["ConversationStore", "RateLimiter"]
