from __future__ import annotations

from ....domain.abuse import AbuseRepository
from .memory import MemoryAbuseStore
from .postgres import PostgresAbuseStore


def AbuseStore(database_url: str | None = None) -> AbuseRepository:
    return PostgresAbuseStore(database_url) if database_url else MemoryAbuseStore()
