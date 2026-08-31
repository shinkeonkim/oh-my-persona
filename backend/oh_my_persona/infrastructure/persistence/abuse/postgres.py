from __future__ import annotations

from datetime import datetime
from typing import cast

from ....domain.abuse import AbuseBlock


class PostgresAbuseStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def initialize(self) -> None:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS abuse_blocks (
                  id uuid PRIMARY KEY, identity_hash char(64), conversation_id uuid,
                  reason text NOT NULL, note text NOT NULL DEFAULT '',
                  blocked_until timestamptz, created_by text NOT NULL,
                  created_at timestamptz NOT NULL DEFAULT now(), revoked_at timestamptz,
                  CHECK (identity_hash IS NOT NULL OR conversation_id IS NOT NULL));
                CREATE INDEX IF NOT EXISTS abuse_blocks_identity_idx
                  ON abuse_blocks(identity_hash) WHERE revoked_at IS NULL;
                CREATE INDEX IF NOT EXISTS abuse_blocks_conversation_idx
                  ON abuse_blocks(conversation_id) WHERE revoked_at IS NULL;
            """)

    def create(self, block: AbuseBlock) -> AbuseBlock:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """INSERT INTO abuse_blocks
                (id,identity_hash,conversation_id,reason,note,blocked_until,created_by,created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (block.id, block.identity_hash, block.conversation_id, block.reason,
                 block.note, block.blocked_until, block.created_by, block.created_at),
            )
        return block

    def active_for(self, identity_hash: str, conversation_id: str | None) -> AbuseBlock | None:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                """SELECT id,identity_hash,conversation_id,reason,note,blocked_until,
                created_by,created_at,revoked_at FROM abuse_blocks
                WHERE revoked_at IS NULL AND (blocked_until IS NULL OR blocked_until > now())
                AND ((%s <> '' AND identity_hash=%s)
                  OR (%s::uuid IS NOT NULL AND conversation_id=%s::uuid))
                ORDER BY created_at DESC LIMIT 1""",
                (identity_hash, identity_hash, conversation_id, conversation_id),
            ).fetchone()
        return _block(row) if row else None

    def list(self, include_revoked: bool = True) -> list[AbuseBlock]:
        import psycopg

        where = "" if include_revoked else "WHERE revoked_at IS NULL"
        with psycopg.connect(self.database_url) as connection:
            rows = connection.execute(
                f"""SELECT id,identity_hash,conversation_id,reason,note,blocked_until,
                created_by,created_at,revoked_at FROM abuse_blocks {where}
                ORDER BY created_at DESC LIMIT 500"""
            ).fetchall()
        return [_block(row) for row in rows]

    def revoke(self, block_id: str) -> AbuseBlock | None:
        import psycopg

        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                """UPDATE abuse_blocks SET revoked_at=now() WHERE id=%s AND revoked_at IS NULL
                RETURNING id,identity_hash,conversation_id,reason,note,blocked_until,
                created_by,created_at,revoked_at""", (block_id,),
            ).fetchone()
        return _block(row) if row else None


def _block(row: tuple[object, ...]) -> AbuseBlock:
    return AbuseBlock(
        id=str(row[0]), identity_hash=str(row[1]).strip() if row[1] else None,
        conversation_id=str(row[2]) if row[2] else None, reason=str(row[3]),
        note=str(row[4]), blocked_until=row[5] if isinstance(row[5], datetime) else None,
        created_by=str(row[6]), created_at=cast(datetime, row[7]),
        revoked_at=row[8] if isinstance(row[8], datetime) else None,
    )
