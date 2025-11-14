-- ============================================================================
-- Manual Glyph Lexicon Sync Script
-- ============================================================================
-- This script populates glyph_lexicon with data from the validated JSON file
-- Run this in Supabase SQL Editor (it uses service_role automatically)
-- ============================================================================

-- First, let's see current count
SELECT COUNT(*) as current_count FROM glyph_lexicon;

-- Option 1: If you want to replace all existing glyphs (recommended)
-- TRUNCATE glyph_lexicon;

-- Option 2: Just delete the test data and keep structure
DELETE FROM glyph_lexicon;

-- Now you need to:
-- 1. Export glyph_lexicon_rows_validated.json to CSV format
-- 2. Use Supabase Dashboard → Table Editor → glyph_lexicon → Insert → Import from CSV

-- OR run the Python script below with SERVICE_ROLE_KEY in .env

-- Verify after import
SELECT COUNT(*) as final_count FROM glyph_lexicon;
SELECT * FROM glyph_lexicon LIMIT 5;
