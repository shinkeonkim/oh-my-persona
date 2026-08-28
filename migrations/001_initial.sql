CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS sources (
  id text PRIMARY KEY,
  canonical_url text NOT NULL UNIQUE CHECK (canonical_url LIKE 'https://%'),
  source_type text NOT NULL,
  title text NOT NULL,
  publisher text,
  published_at timestamptz,
  updated_at timestamptz,
  observed_at timestamptz NOT NULL,
  trust text NOT NULL,
  status text NOT NULL CHECK (status IN ('accepted','review','rejected','tombstoned')),
  metadata jsonb NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id text NOT NULL REFERENCES sources(id),
  content_sha256 char(64) NOT NULL,
  mime_type text NOT NULL,
  language text,
  extractor_version text NOT NULL,
  public_scope text NOT NULL DEFAULT 'public',
  content text NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}',
  UNIQUE(source_id, content_sha256)
);

CREATE TABLE IF NOT EXISTS claims (
  id text PRIMARY KEY,
  subject text NOT NULL,
  predicate text NOT NULL,
  object_text text NOT NULL,
  valid_from date,
  valid_to date,
  date_precision text NOT NULL CHECK (date_precision IN ('day','month','year','unknown')),
  kind text NOT NULL,
  confidence text NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS claim_sources (
  claim_id text REFERENCES claims(id) ON DELETE CASCADE,
  source_id text REFERENCES sources(id),
  PRIMARY KEY(claim_id, source_id)
);

CREATE TABLE IF NOT EXISTS chunks (
  id text PRIMARY KEY,
  document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  ordinal integer NOT NULL,
  section text,
  page integer,
  content text NOT NULL,
  content_sha256 char(64) NOT NULL,
  token_count integer,
  search_vector tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED,
  metadata jsonb NOT NULL DEFAULT '{}',
  UNIQUE(document_id, ordinal),
  UNIQUE(content_sha256)
);

CREATE INDEX IF NOT EXISTS chunks_search_idx ON chunks USING gin(search_vector);

CREATE TABLE IF NOT EXISTS embeddings (
  chunk_id text REFERENCES chunks(id) ON DELETE CASCADE,
  model text NOT NULL,
  dimension integer NOT NULL CHECK (dimension = 1536),
  embedding vector(1536) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(chunk_id, model)
);

CREATE INDEX IF NOT EXISTS embeddings_cosine_idx ON embeddings USING hnsw (embedding vector_cosine_ops);
