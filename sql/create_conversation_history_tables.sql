-- SQL DDL for conversation_history and deletion_audit tables
-- Intended for Supabase (Postgres)

-- Enable pgcrypto for gen_random_uuid() if not already enabled
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Main conversation history table
CREATE TABLE IF NOT EXISTS public.conversation_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text,
    username text,
    user_message text,
    assistant_reply text,
    processing_time text,
    mode text,
    timestamp timestamptz DEFAULT now(),
    metadata jsonb DEFAULT '{}',
    -- optional: index for faster lookups by user
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_conversation_history_user_id ON public.conversation_history (user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_history_timestamp ON public.conversation_history (timestamp DESC);

-- Deletion audit table to record deletion requests for user sovereignty
CREATE TABLE IF NOT EXISTS public.conversation_deletion_audit (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text,
    requested_at timestamptz DEFAULT now(),
    requested_by text,
    method text,
    details jsonb DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_deletion_audit_user_id ON public.conversation_deletion_audit (user_id);

-- Helpful grant (optional): allow anon API key to insert into conversation_history only
-- Note: adapt roles and security according to your Supabase Row Level Security policies.
