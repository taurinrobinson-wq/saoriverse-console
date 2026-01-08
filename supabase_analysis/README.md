# Supabase Database Analysis

This directory contains exported data and schemas from your Supabase database for analysis.

## Directory Structure

```text
```


supabase_analysis/
├── tables/          # Place exported table data (CSV, JSON, or SQL dumps)
├── schemas/         # Place table schema definitions (DDL/structure exports)
└── README.md        # This file

```



## How to Export Your Tables

### Option 1: Export via Supabase Dashboard (Recommended)

**For Table Data:**

1. Go to Supabase Dashboard → Table Editor
2. Select each table
3. Click "..." menu → Export as CSV
4. Save to `supabase_analysis/tables/[table_name].csv`

**For Table Schemas:**

1. Go to Supabase Dashboard → SQL Editor
2. Run this query for each table:

   ```sql
SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE
table_schema = 'public' AND table_name = 'your_table_name' ORDER BY ordinal_position;
   ```

3. Export results to `supabase_analysis/schemas/[table_name]_schema.csv`

### Option 2: Export Complete Schema (All Tables)

Run this in Supabase SQL Editor:

```sql


-- Get all table structures
SELECT table_name, column_name, data_type, character_maximum_length, is_nullable, column_default
FROM information_schema.columns WHERE table_schema = 'public'

```text
```


Save result to: `supabase_analysis/schemas/complete_schema.csv`

### Option 3: Quick Table List

Get a list of all your tables:

```sql
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```


## What to Export

**Essential tables to export:**

- `glyphs` - Glyph lexicon data
- `glyph_logs` - Usage logs
- `emotional_tags` - Tag definitions
- `conversations` - Conversation history
- `conversation_messages` - Message data
- `users` - User accounts
- Any other custom tables you've created

## Analysis Goals

Once you've placed the files here, I will:

1. ✅ Map each table to your codebase usage 2. ✅ Identify unused/redundant tables 3. ✅ Suggest column
optimizations 4. ✅ Recommend safe deletions 5. ✅ Verify schema matches code expectations 6. ✅
Identify missing indexes or constraints

## Notes

- Data exports should be small samples (first 100-1000 rows is fine)
- Schema exports should be complete (all columns/constraints)
- Include foreign key relationships if possible
