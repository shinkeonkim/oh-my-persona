CREATE TABLE IF NOT EXISTS abuse_blocks (
  id uuid PRIMARY KEY,
  identity_hash char(64),
  conversation_id uuid,
  reason text NOT NULL,
  note text NOT NULL DEFAULT '',
  blocked_until timestamptz,
  created_by text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  revoked_at timestamptz,
  CHECK (identity_hash IS NOT NULL OR conversation_id IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS abuse_blocks_identity_idx
  ON abuse_blocks(identity_hash) WHERE revoked_at IS NULL;
CREATE INDEX IF NOT EXISTS abuse_blocks_conversation_idx
  ON abuse_blocks(conversation_id) WHERE revoked_at IS NULL;
