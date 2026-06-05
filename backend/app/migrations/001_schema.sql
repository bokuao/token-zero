-- =========================================================
-- TokenZero Schema — Run in Supabase SQL Editor
-- =========================================================

-- 1. PROVIDERS
CREATE TABLE IF NOT EXISTS t0_providers (
  id         TEXT PRIMARY KEY,
  name       TEXT NOT NULL,
  status     TEXT NOT NULL DEFAULT 'active'
             CHECK (status IN ('active','degraded','deprecated')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. MODELS
CREATE TABLE IF NOT EXISTS t0_models (
  id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  provider_id      TEXT NOT NULL REFERENCES t0_providers(id) ON DELETE CASCADE,
  model_id         TEXT NOT NULL,
  display_name     TEXT,
  description      TEXT,
  context_length   INTEGER,
  max_output       INTEGER,
  input_modalities TEXT[] NOT NULL DEFAULT '{text}',
  capabilities     TEXT[] NOT NULL DEFAULT '{}',
  is_free          BOOLEAN NOT NULL DEFAULT FALSE,
  pricing          JSONB,
  rate_limits      JSONB,
  first_seen_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  free_since       TIMESTAMPTZ,
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  source           TEXT NOT NULL DEFAULT 'api'
                   CHECK (source IN ('api','curated')),
  meta             JSONB NOT NULL DEFAULT '{}',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (provider_id, model_id)
);

CREATE INDEX IF NOT EXISTS idx_t0_models_free_active ON t0_models (is_free, is_active);
CREATE INDEX IF NOT EXISTS idx_t0_models_provider    ON t0_models (provider_id);
CREATE INDEX IF NOT EXISTS idx_t0_models_caps        ON t0_models USING GIN (capabilities);
CREATE INDEX IF NOT EXISTS idx_t0_models_last_seen   ON t0_models (last_seen_at DESC);

-- 3. COLLECTION_RUNS
CREATE TABLE IF NOT EXISTS t0_collection_runs (
  id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  provider_id  TEXT REFERENCES t0_providers(id),
  started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at  TIMESTAMPTZ,
  status       TEXT NOT NULL DEFAULT 'running'
               CHECK (status IN ('running','success','partial','failed')),
  models_found INTEGER,
  error        TEXT,
  meta         JSONB NOT NULL DEFAULT '{}'
);

-- 4. MODEL_EVENTS
CREATE TABLE IF NOT EXISTS t0_model_events (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  model_id    BIGINT NOT NULL REFERENCES t0_models(id) ON DELETE CASCADE,
  event_type  TEXT NOT NULL
              CHECK (event_type IN ('appeared','became_free','became_paid','disappeared','reappeared')),
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  detail      JSONB
);
CREATE INDEX IF NOT EXISTS idx_t0_events_model ON t0_model_events (model_id, occurred_at DESC);

-- Seed providers
INSERT INTO t0_providers (id, name) VALUES
  ('openrouter', 'OpenRouter'),
  ('google', 'Google AI Studio'),
  ('groq', 'Groq'),
  ('cerebras', 'Cerebras'),
  ('mistral', 'Mistral AI')
ON CONFLICT (id) DO NOTHING;
