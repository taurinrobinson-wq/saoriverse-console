-- Migration: Create conversations table for conversation persistence
-- Run this in Supabase SQL editor or via psql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.conversations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id text,
  user_id text NOT NULL,
  title text,
  messages jsonb NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  last_activity timestamptz NOT NULL DEFAULT now()
);

-- Prevent duplicates for client-provided conversation ids per user
CREATE UNIQUE INDEX IF NOT EXISTS conversations_conversation_id_user_id_uniq
  ON public.conversations (conversation_id, user_id);

-- GIN index to speed JSONB queries against messages
CREATE INDEX IF NOT EXISTS conversations_messages_gin
  ON public.conversations USING gin (messages jsonb_path_ops);

-- Row-level security should be enabled and policies created if you plan to
-- allow direct client writes. For server-side writes with a service role key
-- you can omit RLS or keep it but ensure the server uses the service role.
