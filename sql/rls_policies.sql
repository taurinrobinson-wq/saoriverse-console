-- Row-Level Security (RLS) example policies for conversation_history and deletion audit
-- Adjust auth.uid() usage to the claim you use for user_id if different

-- Enable RLS on conversation_history
ALTER TABLE IF EXISTS public.conversation_history ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to insert their own rows (auth.uid() should match user_id)
CREATE POLICY IF NOT EXISTS "insert_own_conversation" ON public.conversation_history
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Allow authenticated users to select only their rows
CREATE POLICY IF NOT EXISTS "select_own_conversation" ON public.conversation_history
  FOR SELECT USING (auth.uid() = user_id);

-- Allow authenticated users to delete only their rows
CREATE POLICY IF NOT EXISTS "delete_own_conversation" ON public.conversation_history
  FOR DELETE USING (auth.uid() = user_id);

-- Optionally restrict updates so users cannot modify assistant replies
CREATE POLICY IF NOT EXISTS "update_own_conversation" ON public.conversation_history
  FOR UPDATE USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- RLS for deletion audit: allow insert by server role or authenticated services only
ALTER TABLE IF EXISTS public.conversation_deletion_audit ENABLE ROW LEVEL SECURITY;

-- If you want the authenticated user to be able to insert audit rows for their own deletion actions:
CREATE POLICY IF NOT EXISTS "insert_own_deletion_audit" ON public.conversation_deletion_audit
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Prevent public from selecting audit rows by default (no select policy)

-- Notes:
-- 1) These policies assume your JWT `sub` claim maps to `auth.uid()` and that value equals the stored `user_id`.
-- 2) If your app uses a different claim (e.g., 'email'), change checks accordingly: (auth.jwt() -> auth.jwt() -> JSON extraction).
-- 3) Test policies in the Supabase SQL editor and adapt to your auth flow.
