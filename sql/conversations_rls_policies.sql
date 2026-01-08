-- Row Level Security (RLS) Policies for Conversations Table
-- Restricts access so users can only view/modify their own conversations

-- Enable RLS on conversations table
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;

-- Policy 1: Users can SELECT only their own conversations
CREATE POLICY "Users can select own conversations"
ON public.conversations
FOR SELECT
USING (auth.uid()::text = user_id);

-- Policy 2: Users can INSERT only their own conversations
CREATE POLICY "Users can insert own conversations"
ON public.conversations
FOR INSERT
WITH CHECK (auth.uid()::text = user_id);

-- Policy 3: Users can UPDATE only their own conversations
CREATE POLICY "Users can update own conversations"
ON public.conversations
FOR UPDATE
USING (auth.uid()::text = user_id)
WITH CHECK (auth.uid()::text = user_id);

-- Policy 4: Users can DELETE only their own conversations
CREATE POLICY "Users can delete own conversations"
ON public.conversations
FOR DELETE
USING (auth.uid()::text = user_id);

-- ============================================================================
-- Row Level Security (RLS) Policies for Conversation Metadata Table
-- ============================================================================

-- Enable RLS on conversation_metadata table
ALTER TABLE public.conversation_metadata ENABLE ROW LEVEL SECURITY;

-- Policy 1: Users can SELECT their own conversation metadata
CREATE POLICY "Users can select own metadata"
ON public.conversation_metadata
FOR SELECT
USING (auth.uid()::text = user_id);

-- Policy 2: Users can INSERT their own conversation metadata
-- (Only the system/app should do this, but allow for app flexibility)
CREATE POLICY "Users can insert own metadata"
ON public.conversation_metadata
FOR INSERT
WITH CHECK (auth.uid()::text = user_id);

-- Policy 3: Users can UPDATE their own conversation metadata
CREATE POLICY "Users can update own metadata"
ON public.conversation_metadata
FOR UPDATE
USING (auth.uid()::text = user_id)
WITH CHECK (auth.uid()::text = user_id);

-- Policy 4: Users can DELETE their own conversation metadata
CREATE POLICY "Users can delete own metadata"
ON public.conversation_metadata
FOR DELETE
USING (auth.uid()::text = user_id);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- To verify RLS is enabled and policies are in place, run:
-- 
-- SELECT tablename FROM pg_tables 
-- WHERE tablename IN ('conversations', 'conversation_metadata');
--
-- SELECT schemaname, tablename, rowsecurity 
-- FROM pg_tables 
-- WHERE tablename IN ('conversations', 'conversation_metadata');
--
-- SELECT tablename, policyname, qual, with_check 
-- FROM pg_policies 
-- WHERE tablename IN ('conversations', 'conversation_metadata')
-- ORDER BY tablename, policyname;

-- ============================================================================
-- IMPORTANT NOTES
-- ============================================================================
-- 
-- 1. RLS restricts access at the database level
-- 2. Users can only see/modify their own (user_id = auth.uid()) conversations
-- 3. The auth.uid() function requires a valid JWT token from Supabase Auth
-- 4. Service role key bypasses RLS (use for admin operations only)
-- 5. Anon key respects RLS (use for client-side operations)
--
-- If you're NOT using Supabase Auth, you'll need to modify these policies
-- to use your own user_id column and authentication method.
--
-- ============================================================================
