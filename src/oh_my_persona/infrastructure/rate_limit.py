from __future__ import annotations

import os
import threading
from datetime import UTC, datetime, timedelta
from typing import Any


class RateLimiter:
    def __init__(self, store: Any, limit: int | None = None, window_seconds: int | None = None):
        self.store = store
        self.limit = limit or int(os.environ.get("PERSONA_RATE_LIMIT", "12"))
        self.window_seconds = window_seconds or int(
            os.environ.get("PERSONA_RATE_WINDOW_SECONDS", "3600")
        )
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
            cursor.execute(
                "INSERT INTO rate_limit_events(identity_hash) VALUES (%s)", (identity_hash,)
            )
            cursor.execute(
                "DELETE FROM rate_limit_events WHERE created_at < now() - interval '2 days'"
            )
        return True, 0
