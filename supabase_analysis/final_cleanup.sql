-- ============================================================================
-- Final Cleanup Tasks
-- ============================================================================
-- Run this in Supabase SQL Editor to complete the database setup
-- ============================================================================

-- 1. Drop the backup table (no longer needed)
DROP TABLE IF EXISTS conversations_backup_20251108;

-- 2. Verify glyph_lexicon count
SELECT COUNT(*) as glyph_count FROM glyph_lexicon;
-- Expected: 6434

-- 3. Check for any empty tables that might need data
SELECT 
  schemaname,
  tablename,
  n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;

-- 4. Verify RLS is enabled on key tables
SELECT 
  schemaname, 
  tablename, 
  rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- Success message
SELECT '✅ Cleanup complete!' as status;
