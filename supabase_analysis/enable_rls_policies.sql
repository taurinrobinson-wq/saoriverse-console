-- ============================================================================
-- Row Level Security (RLS) Policies for Emotional OS
-- ============================================================================
-- This script enables RLS and creates policies for user data isolation
-- Run this in your Supabase SQL Editor
-- ============================================================================

-- ============================================================================
-- 1. USER-SPECIFIC TABLES (Require user_id matching)
-- ============================================================================

-- conversations: Each user sees only their own conversations
-- ----------------------------------------------------------------------------
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (idempotent)
DROP POLICY IF EXISTS "Users view own conversations" ON conversations;
DROP POLICY IF EXISTS "Users insert own conversations" ON conversations;
DROP POLICY IF EXISTS "Users update own conversations" ON conversations;
DROP POLICY IF EXISTS "Users delete own conversations" ON conversations;

-- Create policies
CREATE POLICY "Users view own conversations" ON conversations
  FOR SELECT
  USING (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users insert own conversations" ON conversations
  FOR INSERT
  WITH CHECK (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users update own conversations" ON conversations
  FOR UPDATE
  USING (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub')
  WITH CHECK (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users delete own conversations" ON conversations
  FOR DELETE
  USING (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- conversation_messages: Messages belong to conversations (inherit user_id check)
-- ----------------------------------------------------------------------------
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users view own messages" ON conversation_messages;
DROP POLICY IF EXISTS "Users insert own messages" ON conversation_messages;
DROP POLICY IF EXISTS "Users update own messages" ON conversation_messages;
DROP POLICY IF EXISTS "Users delete own messages" ON conversation_messages;

-- Check via conversation_id FK relationship
CREATE POLICY "Users view own messages" ON conversation_messages
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM conversations 
      WHERE conversations.conversation_id = conversation_messages.conversation_id
        AND (conversations.user_id::text = auth.uid()::text 
             OR conversations.user_id::text = current_setting('request.jwt.claims', true)::json->>'sub')
    )
  );

CREATE POLICY "Users insert own messages" ON conversation_messages
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM conversations 
      WHERE conversations.conversation_id = conversation_messages.conversation_id
        AND (conversations.user_id::text = auth.uid()::text 
             OR conversations.user_id::text = current_setting('request.jwt.claims', true)::json->>'sub')
    )
  );

CREATE POLICY "Users update own messages" ON conversation_messages
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM conversations 
      WHERE conversations.conversation_id = conversation_messages.conversation_id
        AND (conversations.user_id::text = auth.uid()::text 
             OR conversations.user_id::text = current_setting('request.jwt.claims', true)::json->>'sub')
    )
  );

CREATE POLICY "Users delete own messages" ON conversation_messages
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM conversations 
      WHERE conversations.conversation_id = conversation_messages.conversation_id
        AND (conversations.user_id::text = auth.uid()::text 
             OR conversations.user_id::text = current_setting('request.jwt.claims', true)::json->>'sub')
    )
  );

-- conversation_metadata: Audit trail for conversations
-- ----------------------------------------------------------------------------
ALTER TABLE conversation_metadata ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users view own metadata" ON conversation_metadata;
DROP POLICY IF EXISTS "Users insert own metadata" ON conversation_metadata;

CREATE POLICY "Users view own metadata" ON conversation_metadata
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM conversations 
      WHERE conversations.conversation_id = conversation_metadata.conversation_id
        AND (conversations.user_id::text = auth.uid()::text 
             OR conversations.user_id::text = current_setting('request.jwt.claims', true)::json->>'sub')
    )
  );

CREATE POLICY "Users insert own metadata" ON conversation_metadata
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM conversations 
      WHERE conversations.conversation_id = conversation_metadata.conversation_id
        AND (conversations.user_id::text = auth.uid()::text 
             OR conversations.user_id::text = current_setting('request.jwt.claims', true)::json->>'sub')
    )
  );

-- glyph_logs: User interaction logs
-- ----------------------------------------------------------------------------
ALTER TABLE glyph_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users view own logs" ON glyph_logs;
DROP POLICY IF EXISTS "Users insert own logs" ON glyph_logs;

CREATE POLICY "Users view own logs" ON glyph_logs
  FOR SELECT
  USING (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users insert own logs" ON glyph_logs
  FOR INSERT
  WITH CHECK (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- glyphs: User-created glyphs (learned during conversations)
-- ----------------------------------------------------------------------------
ALTER TABLE glyphs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users view own glyphs" ON glyphs;
DROP POLICY IF EXISTS "Users insert own glyphs" ON glyphs;
DROP POLICY IF EXISTS "Users update own glyphs" ON glyphs;
DROP POLICY IF EXISTS "Users delete own glyphs" ON glyphs;

CREATE POLICY "Users view own glyphs" ON glyphs
  FOR SELECT
  USING (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users insert own glyphs" ON glyphs
  FOR INSERT
  WITH CHECK (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users update own glyphs" ON glyphs
  FOR UPDATE
  USING (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub')
  WITH CHECK (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users delete own glyphs" ON glyphs
  FOR DELETE
  USING (user_id::text = auth.uid()::text OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- messages: General message table (if user_id exists)
-- ----------------------------------------------------------------------------
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users view own messages table" ON messages;
DROP POLICY IF EXISTS "Users insert own messages table" ON messages;

-- Note: Adjust these if messages table doesn't have user_id column
CREATE POLICY "Users view own messages table" ON messages
  FOR SELECT
  USING (
    -- If user_id column exists
    user_id::text = auth.uid()::text 
    OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub'
    -- Or allow all if no user_id (adjust as needed)
    OR user_id IS NULL
  );

CREATE POLICY "Users insert own messages table" ON messages
  FOR INSERT
  WITH CHECK (
    user_id::text = auth.uid()::text 
    OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub'
    OR user_id IS NULL
  );

-- users: Users can only see their own profile
-- ----------------------------------------------------------------------------
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users view own profile" ON users;
DROP POLICY IF EXISTS "Users update own profile" ON users;

CREATE POLICY "Users view own profile" ON users
  FOR SELECT
  USING (id::text = auth.uid()::text OR id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users update own profile" ON users
  FOR UPDATE
  USING (id::text = auth.uid()::text OR id::text = current_setting('request.jwt.claims', true)::json->>'sub')
  WITH CHECK (id::text = auth.uid()::text OR id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- ============================================================================
-- 2. SHARED/READ-ONLY TABLES (Public read, service_role write)
-- ============================================================================

-- glyph_lexicon: Shared emotional glyph definitions (6,434 glyphs)
-- ----------------------------------------------------------------------------
ALTER TABLE glyph_lexicon ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Everyone can read glyph_lexicon" ON glyph_lexicon;
DROP POLICY IF EXISTS "Service role can manage glyph_lexicon" ON glyph_lexicon;

-- Allow all authenticated users to read
CREATE POLICY "Everyone can read glyph_lexicon" ON glyph_lexicon
  FOR SELECT
  USING (true);

-- Only service_role can insert/update/delete
CREATE POLICY "Service role can manage glyph_lexicon" ON glyph_lexicon
  FOR ALL
  USING (auth.jwt()->>'role' = 'service_role')
  WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- emotional_tags: Shared tag definitions
-- ----------------------------------------------------------------------------
ALTER TABLE emotional_tags ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Everyone can read emotional_tags" ON emotional_tags;
DROP POLICY IF EXISTS "Service role can manage emotional_tags" ON emotional_tags;

CREATE POLICY "Everyone can read emotional_tags" ON emotional_tags
  FOR SELECT
  USING (true);

CREATE POLICY "Service role can manage emotional_tags" ON emotional_tags
  FOR ALL
  USING (auth.jwt()->>'role' = 'service_role')
  WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- ritual_triggers: Shared ritual definitions
-- ----------------------------------------------------------------------------
ALTER TABLE ritual_triggers ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Everyone can read ritual_triggers" ON ritual_triggers;
DROP POLICY IF EXISTS "Service role can manage ritual_triggers" ON ritual_triggers;

CREATE POLICY "Everyone can read ritual_triggers" ON ritual_triggers
  FOR SELECT
  USING (true);

CREATE POLICY "Service role can manage ritual_triggers" ON ritual_triggers
  FOR ALL
  USING (auth.jwt()->>'role' = 'service_role')
  WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- symbolic_interpreter: Shared symbolic mappings
-- ----------------------------------------------------------------------------
ALTER TABLE symbolic_interpreter ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Everyone can read symbolic_interpreter" ON symbolic_interpreter;
DROP POLICY IF EXISTS "Service role can manage symbolic_interpreter" ON symbolic_interpreter;

CREATE POLICY "Everyone can read symbolic_interpreter" ON symbolic_interpreter
  FOR SELECT
  USING (true);

CREATE POLICY "Service role can manage symbolic_interpreter" ON symbolic_interpreter
  FOR ALL
  USING (auth.jwt()->>'role' = 'service_role')
  WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- 3. SPECIAL CASES
-- ============================================================================

-- glyph_trail: User interaction trail (if user_id exists)
-- ----------------------------------------------------------------------------
ALTER TABLE glyph_trail ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users view own trail" ON glyph_trail;
DROP POLICY IF EXISTS "Users insert own trail" ON glyph_trail;

CREATE POLICY "Users view own trail" ON glyph_trail
  FOR SELECT
  USING (
    user_id::text = auth.uid()::text 
    OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub'
    OR user_id IS NULL  -- Allow if no user_id (public trails)
  );

CREATE POLICY "Users insert own trail" ON glyph_trail
  FOR INSERT
  WITH CHECK (
    user_id::text = auth.uid()::text 
    OR user_id::text = current_setting('request.jwt.claims', true)::json->>'sub'
    OR user_id IS NULL
  );

-- rupture_named: Special glyph type (likely shared read-only)
-- ----------------------------------------------------------------------------
ALTER TABLE rupture_named ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Everyone can read rupture_named" ON rupture_named;
DROP POLICY IF EXISTS "Service role can manage rupture_named" ON rupture_named;

CREATE POLICY "Everyone can read rupture_named" ON rupture_named
  FOR SELECT
  USING (true);

CREATE POLICY "Service role can manage rupture_named" ON rupture_named
  FOR ALL
  USING (auth.jwt()->>'role' = 'service_role')
  WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- ============================================================================
-- 4. BACKUP TABLES (Keep disabled or drop)
-- ============================================================================

-- conversations_backup_20251108: Backup table - NO RLS NEEDED
-- You can either:
-- Option A: Leave RLS disabled (default)
-- Option B: Drop the table if backup is no longer needed
-- 
-- To drop: DROP TABLE IF EXISTS conversations_backup_20251108;

-- ============================================================================
-- 5. VERIFICATION QUERIES
-- ============================================================================

-- Check which tables have RLS enabled
-- Run this to verify:
/*
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
*/

-- Check all policies
-- Run this to see all policies:
/*
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
*/

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. Service role bypasses RLS automatically
-- 2. Edge functions using service_role_key can read/write all data
-- 3. Client SDK using anon_key respects RLS policies
-- 4. Demo users (no auth.uid()) won't match these policies
--    - You may need separate "demo mode" policies or disable RLS for demo
-- 5. Adjust user_id column types if they're UUID instead of TEXT
-- ============================================================================

COMMIT;
