ALTER TABLE conversation_messages
  DROP CONSTRAINT IF EXISTS conversation_messages_role_check;

ALTER TABLE conversation_messages
  ADD CONSTRAINT conversation_messages_role_check
  CHECK (role IN ('user', 'assistant', 'owner'));

CREATE INDEX IF NOT EXISTS conversations_discord_thread_idx
  ON conversations ((metadata->>'discord_thread_id'))
  WHERE metadata ? 'discord_thread_id';
