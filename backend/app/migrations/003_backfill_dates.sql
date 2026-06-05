-- Backfill: set all current models to 3 days ago
-- so only genuinely new models (from future collector runs) get the NEW badge
UPDATE t0_models
SET first_seen_at = now() - INTERVAL '3 days'
WHERE first_seen_at > now() - INTERVAL '1 day';
