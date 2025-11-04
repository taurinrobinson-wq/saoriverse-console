-- SQL DDL for conversations table
-- Persistent conversation storage with metadata and auto-naming
-- Intended for Supabase (Postgres)

-- Enable pgcrypto if not already enabled
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Main conversations table
-- Stores full conversations with metadata for retrieval and management
CREATE TABLE IF NOT EXISTS public.conversations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text NOT NULL,
    conversation_id text NOT NULL,
    title text NOT NULL DEFAULT 'New Conversation',
    messages jsonb NOT NULL DEFAULT '[]',
    processing_mode text DEFAULT 'hybrid',
    message_count integer DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    -- Store first message for context/analytics
    first_message text,
    -- Store first assistant response for context
    first_response text,
    -- For future use: store emotional context/tags extracted from conversation
    emotional_context jsonb DEFAULT '{}',
    -- For future use: store key topics/themes
    topics jsonb DEFAULT '[]',
    -- Soft delete flag
    archived boolean DEFAULT false
);

-- Create unique constraint on (user_id, conversation_id) for upsert operations
CREATE UNIQUE INDEX IF NOT EXISTS idx_conversations_user_conversation 
ON public.conversations (user_id, conversation_id);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
ON public.conversations (user_id);

CREATE INDEX IF NOT EXISTS idx_conversations_updated_at 
ON public.conversations (updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_created_at 
ON public.conversations (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_archived 
ON public.conversations (archived) WHERE NOT archived;

-- Conversation metadata table for tracking renames and operations
CREATE TABLE IF NOT EXISTS public.conversation_metadata (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id text NOT NULL,
    conversation_id text NOT NULL,
    action text NOT NULL, -- 'created', 'renamed', 'deleted', 'archived', 'restored'
    details jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_conversation_metadata_user_id 
ON public.conversation_metadata (user_id);

CREATE INDEX IF NOT EXISTS idx_conversation_metadata_conversation_id 
ON public.conversation_metadata (conversation_id);

-- Helper function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS conversations_update_updated_at ON public.conversations;
CREATE TRIGGER conversations_update_updated_at
BEFORE UPDATE ON public.conversations
FOR EACH ROW
EXECUTE FUNCTION update_conversation_updated_at();
