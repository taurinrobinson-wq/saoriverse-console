BEGIN;
CREATE EXTENSION IF NOT EXISTS pgtap WITH SCHEMA extensions;

SELECT plan(2);

-- ✅ Table exists
SELECT has_table('public', 'glyphs');

-- ✅ Column exists
SELECT has_column('public', 'glyphs', 'symbolic_pairing');

ROLLBACK;