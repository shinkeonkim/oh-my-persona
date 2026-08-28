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
                  role text NOT NULL CHECK (role IN ('user','assistant')), content text NOT NULL,
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
            """)

    def create(self) -> str:
        conversation_id = str(uuid.uuid4())
        if not self.database_url:
            with self._lock:
                self._memory[conversation_id] = []
            return conversation_id
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute("INSERT INTO conversations(id) VALUES (%s)", (conversation_id,))
        return conversation_id

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
            {"role": row[0], "content": row[1], "model": row[2], "sources": row[3],
             "created_at": row[4].isoformat()}
            for row in rows
        ]

    def append(self, conversation_id: str, role: str, content: str, model: str | None = None,
               sources: list[dict] | None = None) -> None:
        created_at = datetime.now(UTC).isoformat()
        item = {"role": role, "content": content, "model": model,
                "sources": sources or [], "created_at": created_at}
        if not self.database_url:
            with self._lock:
                self._memory.setdefault(conversation_id, []).append(item)
            return
        import psycopg

        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO conversation_messages(conversation_id,role,content,model,sources)
                   VALUES (%s,%s,%s,%s,%s::jsonb)""",
                (conversation_id, role, content, model, json.dumps(sources or [], ensure_ascii=False)),
            )
            cursor.execute("UPDATE conversations SET updated_at=now() WHERE id=%s", (conversation_id,))


class RateLimiter:
    def __init__(self, store: ConversationStore, limit: int | None = None, window_seconds: int | None = None):
        self.store = store
        self.limit = limit or int(os.environ.get("PERSONA_RATE_LIMIT", "12"))
        self.window_seconds = window_seconds or int(os.environ.get("PERSONA_RATE_WINDOW_SECONDS", "3600"))
        self._events: dict[str, list[datetime]] = {}
        self._lock = threading.Lock()

    def consume(self, identity_hash: str) -> tuple[bool, int]:
        cutoff = datetime.now(UTC) - timedelta(seconds=self.window_seconds)
        if not self.store.database_url:
            with self._lock:
                events = [event for event in self._events.get(identity_hash, []) if event > cutoff]
                if len(events) >= self.limit:
                    retry = max(1, int((events[0] - cutoff).total_seconds()))
                    self._events[identity_hash] = events
                    return False, retry
                events.append(datetime.now(UTC))
                self._events[identity_hash] = events
                return True, 0
        import psycopg

        with psycopg.connect(self.store.database_url) as connection, connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (identity_hash,))
            cursor.execute(
                "SELECT count(*), min(created_at) FROM rate_limit_events WHERE identity_hash=%s AND created_at>%s",
                (identity_hash, cutoff),
            )
            count, oldest = cursor.fetchone()
            if count >= self.limit:
                return False, max(1, int((oldest - cutoff).total_seconds()))
            cursor.execute("INSERT INTO rate_limit_events(identity_hash) VALUES (%s)", (identity_hash,))
            cursor.execute("DELETE FROM rate_limit_events WHERE created_at < now() - interval '2 days'")
        return True, 0
