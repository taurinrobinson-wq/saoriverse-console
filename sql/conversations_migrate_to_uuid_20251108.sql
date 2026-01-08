-- ======================================================================
-- MIGRATION: Convert public.conversations.user_id (text) -> uuid
-- Then apply uuid-based RLS policies (Option A)
-- Timestamp suffix used for backups: 20251108
-- IMPORTANT: run during maintenance; ensure you have a DB backup/snapshot
-- ======================================================================

-- STEP 0: PRE-CHECK - abort if any non-UUID strings exist in user_id
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM public.conversations
    WHERE user_id IS NOT NULL
      -- Cast to text to allow regex checks whether column is text or already uuid
      AND NOT (user_id::text ~* '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
  ) THEN
    RAISE EXCEPTION 'Migration aborted: found rows in public.conversations with non-UUID user_id values. Fix them or run a mapping step first.';
  END IF;
END;
$$;

-- STEP 1: Create a full backup copy of the conversations table (including constraints/indexes/triggers)
CREATE TABLE IF NOT EXISTS public.conversations_backup_20251108 (LIKE public.conversations INCLUDING ALL);
TRUNCATE public.conversations_backup_20251108;
INSERT INTO public.conversations_backup_20251108 SELECT * FROM public.conversations;

-- STEP 2: Drop indexes that reference user_id (we'll recreate them after the type change)
DROP INDEX IF EXISTS idx_conversations_user_conversation;
DROP INDEX IF EXISTS idx_conversations_user_id;
DROP INDEX IF EXISTS idx_conversations_user_id_uuid;

-- IMPORTANT: drop any RLS policies that depend on user_id BEFORE altering the column type
DROP POLICY IF EXISTS "Users can select own conversations" ON public.conversations;
DROP POLICY IF EXISTS "Users can insert own conversations" ON public.conversations;
DROP POLICY IF EXISTS "Users can update own conversations" ON public.conversations;
DROP POLICY IF EXISTS "Users can delete own conversations" ON public.conversations;

-- STEP 3: Alter column type to uuid using safe cast
ALTER TABLE public.conversations
  ALTER COLUMN user_id TYPE uuid
  USING user_id::uuid;

-- STEP 4: Recreate indexes with uuid column type
-- Unique index on (user_id, conversation_id)
CREATE UNIQUE INDEX IF NOT EXISTS idx_conversations_user_conversation
  ON public.conversations (user_id, conversation_id);

-- Index on user_id
CREATE INDEX IF NOT EXISTS idx_conversations_user_id
  ON public.conversations (user_id);

-- STEP 5: Apply uuid-based RLS policies (Option A)
ALTER TABLE IF EXISTS public.conversations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can select own conversations" ON public.conversations;
DROP POLICY IF EXISTS "Users can insert own conversations" ON public.conversations;
DROP POLICY IF EXISTS "Users can update own conversations" ON public.conversations;
DROP POLICY IF EXISTS "Users can delete own conversations" ON public.conversations;

CREATE POLICY "Users can select own conversations"
  ON public.conversations
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can insert own conversations"
  ON public.conversations
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update own conversations"
  ON public.conversations
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete own conversations"
  ON public.conversations
  FOR DELETE
  TO authenticated
  USING ((SELECT auth.uid()) = user_id);

-- Ensure privileges for authenticated role (run once)
GRANT SELECT, INSERT, UPDATE, DELETE ON public.conversations TO authenticated;

-- STEP 6: Verification
-- Confirm column type changed to uuid
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'conversations' AND column_name = 'user_id';

-- Show policies in place
SELECT schemaname, tablename, policyname, qual, with_check
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'conversations'
ORDER BY policyname;

-- CLEANUP (optional) once you verify everything is OK:
-- DROP TABLE IF EXISTS public.conversations_backup_20251108;
