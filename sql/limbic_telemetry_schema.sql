-- SQL schema for limbic_telemetry table (Postgres / Supabase)
-- Run this in your Supabase SQL editor or psql to create the telemetry table

CREATE TABLE IF NOT EXISTS public.limbic_telemetry (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz NOT NULL,
    message_hash text NOT NULL,
    emotion_detected text,
    glyphs_generated jsonb,
    limbic_decorated boolean DEFAULT false,
    safety_flag boolean DEFAULT false,
    ab_participate boolean DEFAULT false,
    ab_group text,
    user_id text,
    glyphs_count integer,
    latency_ms integer,
    metadata jsonb,
    inserted_at timestamptz DEFAULT now()
);

-- Recommended: create a policy for insert if using anon key (read your Supabase security model)
-- Example: allow inserts from anon role only if they provide a user_id or from server role
-- CREATE POLICY "anon_insert_limbic" ON public.limbic_telemetry
--     FOR INSERT
--     USING (true)
--     WITH CHECK (true);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_limbic_telemetry_message_hash ON public.limbic_telemetry (message_hash);
CREATE INDEX IF NOT EXISTS idx_limbic_telemetry_user_id ON public.limbic_telemetry (user_id);
CREATE INDEX IF NOT EXISTS idx_limbic_telemetry_ts ON public.limbic_telemetry (timestamp);
