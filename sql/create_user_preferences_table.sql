-- Migration: Create user_preferences table for storing simple UI preferences
-- Run this on your Supabase/Postgres instance to enable server-backed preference persistence

CREATE TABLE IF NOT EXISTS public.user_preferences (
    user_id text PRIMARY KEY,
    persist_history boolean DEFAULT false,
    persist_confirmed boolean DEFAULT false,
    updated_at timestamptz DEFAULT now()
);

-- Optional index on updated_at for querying recent changes
CREATE INDEX IF NOT EXISTS idx_user_preferences_updated_at ON public.user_preferences (updated_at);
