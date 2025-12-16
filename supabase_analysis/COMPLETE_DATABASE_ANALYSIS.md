# Supabase Database Analysis Report

**Generated:** November 12, 2025
**Project:** Emotional OS / Saoriverse Console

##

## Executive Summary

Your Supabase database has **14 tables** with only **2 tables actively being used**:

- ✅ **users** (2 rows) - Working
- ⚠️ **glyph_lexicon** (64 rows) - Has data but may need sync with local DB (6,434 glyphs)

**11 tables are empty** and may be safe to delete or need data migration.

##

## Table Analysis

### ✅ ACTIVE TABLES (2)

#### 1. **users**

- **Rows:** 2
- **Status:** ✅ Active and working
- **Purpose:** User authentication and profiles
- **Columns:** id, username, email, password_hash, salt, created_at, last_login, is_active, updated_at, first_name, last_name
- **Code Usage:**
  - `emotional_os/auth/auth_emotional_os.py`
  - `emotional_os/deploy/modules/auth.py`
  - `supabase/functions/auth-manager/index.ts`
- **Recommendation:** ✅ **KEEP** - Essential for authentication
- **RLS Needed:** YES - Users should only see their own profile

#### 2. **glyph_lexicon**

- **Rows:** 64 (⚠️ Should be 6,434!)
- **Status:** ⚠️ Partial data - needs sync
- **Purpose:** Shared emotional glyph definitions used by all users
- **Code Usage:**
  - `emotional_os/core/signal_parser.py` - Queries for glyph matching
  - `emotional_os/glyphs/glyph_learner.py` - References for learning
- **Recommendation:** ⚠️ **KEEP BUT UPDATE** - Sync from `glyph_lexicon_rows_validated.json` (6,434 glyphs)
- **RLS Needed:** YES - Read-only for users, service_role can write

##

### ⚠️ EMPTY TABLES (11) - Need Action

#### 3. **conversations**

- **Rows:** 0
- **Purpose:** User conversation history persistence
- **Code Usage:**
  - `emotional_os/deploy/modules/conversation_manager.py` (lines 291-350)
  - `emotional_os/deploy/modules/ui.py` - Conversation sidebar
  - `sql/create_conversation_history_tables.sql` - Schema definition
- **Recommendation:** ✅ **KEEP** - Will be used when users start conversations
- **RLS Needed:** YES - User isolation required

#### 4. **conversation_messages**

- **Rows:** 0
- **Purpose:** Individual messages within conversations
- **Code Usage:**
  - `emotional_os/deploy/modules/conversation_manager.py`
  - References in conversation loading logic
- **Recommendation:** ✅ **KEEP** - Part of conversation system
- **RLS Needed:** YES - Via conversation_id FK

#### 5. **conversation_metadata**

- **Rows:** 0
- **Purpose:** Audit trail for conversation operations
- **Code Usage:**
  - `sql/create_conversation_history_tables.sql`
  - Tracks: created, renamed, deleted, archived, restored
- **Recommendation:** ✅ **KEEP** - Useful for audit logs
- **RLS Needed:** YES - Via conversation_id FK

#### 6. **glyphs**

- **Rows:** 0
- **Purpose:** User-created glyphs learned from conversations
- **Code Usage:**
  - `emotional_os/glyphs/glyph_learner.py` (lines 200+)
  - `supabase/saori_edge_function.ts` (lines 218-260)
  - `supabase/functions/authenticated-saori/index.ts`
- **Recommendation:** ✅ **KEEP** - Core feature for learning system
- **RLS Needed:** YES - User isolation required

#### 7. **glyph_logs**

- **Rows:** 0
- **Purpose:** Log user interactions and glyph activations
- **Code Usage:**
  - `supabase/saori_edge_function.ts` (line 280)
  - `supabase/functions/auth-manager/index.ts` (line 363)
  - Used for analytics and learning
- **Recommendation:** ✅ **KEEP** - Important for system learning
- **RLS Needed:** YES - User isolation required

#### 8. **emotional_tags**

- **Rows:** 0
- **Purpose:** Shared emotional tag definitions
- **Code Usage:**
  - `supabase/saori_edge_function.ts` (line 117)
  - `emotional_os/deploy/modules/ui.py` - Tag-based processing
- **Recommendation:** ⚠️ **KEEP BUT POPULATE** - Needs initial data
- **RLS Needed:** YES - Read-only for users

#### 9. **glyph_trail**

- **Rows:** 0
- **Purpose:** Track glyph usage patterns over time
- **Code Usage:** Not found in codebase grep
- **Recommendation:** ❓ **UNCLEAR** - May be legacy or future feature
- **RLS Needed:** YES if keeping - User isolation

#### 10. **messages**

- **Rows:** 0
- **Purpose:** Legacy/general message table
- **Code Usage:** Limited references, may overlap with conversation_messages
- **Recommendation:** ❓ **EVALUATE** - Possibly redundant with conversation_messages
- **RLS Needed:** YES if keeping

#### 11. **ritual_triggers**

- **Rows:** 0
- **Purpose:** Ritual definitions for special interactions
- **Code Usage:** Not found in active codebase
- **Recommendation:** ❓ **EVALUATE** - May be future feature or legacy
- **RLS Needed:** YES - Read-only for users

#### 12. **rupture_named**

- **Rows:** 0
- **Purpose:** Special glyph category for "rupture" emotional states
- **Code Usage:** Not found in active codebase
- **Recommendation:** ❓ **EVALUATE** - May be legacy or future feature
- **RLS Needed:** YES - Read-only for users

#### 13. **symbolic_interpreter**

- **Rows:** 0
- **Purpose:** Symbolic mappings for glyph interpretation
- **Code Usage:** Not found in active codebase
- **Recommendation:** ❓ **EVALUATE** - May be future feature or legacy
- **RLS Needed:** YES - Read-only for users

##

### 🗑️ BACKUP TABLES (1)

#### 14. **conversations_backup_20251108**

- **Rows:** 0
- **Purpose:** Backup from November 8, 2025
- **Recommendation:** ❌ **DELETE** - No longer needed, can be dropped safely
- **SQL:** `DROP TABLE IF EXISTS conversations_backup_20251108;`

##

## Critical Issues Found

### 🚨 Issue 1: glyph_lexicon is Missing Data

- **Current:** 64 glyphs
- **Expected:** 6,434 glyphs
- **Impact:** System won't recognize most emotional inputs
- **Fix:** Run the database update script from earlier (already created and tested)

### ⚠️ Issue 2: emotional_tags is Empty

- **Current:** 0 tags
- **Expected:** Tag definitions for emotional processing
- **Impact:** Tag-based processing won't work
- **Fix:** Need to populate from `emotional_tags_rows.sql` or similar source

##

## Recommendations Summary

### ✅ KEEP & ACTIVE (2 tables)

1. **users** - Authentication system (working)
2. **glyph_lexicon** - Core glyphs (needs data sync)

### ✅ KEEP & PREPARE (8 tables - will be used)

3. **conversations** - Conversation persistence
4. **conversation_messages** - Message storage
5. **conversation_metadata** - Audit trail
6. **glyphs** - User-learned glyphs
7. **glyph_logs** - Interaction tracking
8. **emotional_tags** - Tag definitions (needs population)

### ❓ EVALUATE (4 tables - unclear usage)

9. **glyph_trail** - Not referenced in code
10. **messages** - Possibly redundant
11. **ritual_triggers** - Not referenced in code
12. **rupture_named** - Not referenced in code
13. **symbolic_interpreter** - Not referenced in code

### ❌ DELETE (1 table)

14. **conversations_backup_20251108** - Old backup

##

## Action Plan

### Immediate Actions (Do Now)

1. **Update glyph_lexicon**

   ```bash
   # Already have the update script - just needs to run against Supabase
   # Location: Previous Python script that inserted 6,434 glyphs
   ```

2. **Populate emotional_tags**

   ```sql
   # Find and run: emotional_tags_rows.sql
   # Or create tags from your existing tag system
   ```

3. **Delete backup table**

   ```sql
   DROP TABLE IF EXISTS conversations_backup_20251108;
   ```

### Before Enabling RLS (Do Next)

4. **Test each empty table** - Send a test message to verify:
   - conversations gets created
   - conversation_messages gets populated
   - glyph_logs records interaction
   - glyphs learns from conversation

5. **Decide on unclear tables** - Research codebase for:
   - glyph_trail
   - messages
   - ritual_triggers
   - rupture_named
   - symbolic_interpreter

### After Testing (Do Later)

6. **Enable RLS policies** - Run the `enable_rls_policies.sql` script

7. **Add indexes** - Optimize performance:

   ```sql
   CREATE INDEX idx_conversations_user_id ON conversations(user_id);
   CREATE INDEX idx_glyph_logs_user_id ON glyph_logs(user_id);
   CREATE INDEX idx_glyphs_user_id ON glyphs(user_id);
   ```

##

## Column Analysis

### users table - ✅ Looks Good

```text
```

id, username, email, password_hash, salt, created_at,
last_login, is_active, updated_at, first_name, last_name

```



- All columns are used by authentication system
- No changes needed

### glyph_lexicon - Need to verify columns match local DB

Expected columns from local `glyphs.db`:
```text
```text
```

id, voltage_pair, glyph_name, description, gate,
activation_signals, display_name, response_template

```




**Action:** Need to verify Supabase schema matches
##

## Next Steps

1. ✅ **You've already done:** Created `.env` with correct URLs
2. ⏳ **Do next:** Update `glyph_lexicon` in Supabase (from 64 → 6,434 glyphs)
3. ⏳ **Then:** Populate `emotional_tags` table
4. ⏳ **Then:** Delete `conversations_backup_20251108`
5. ⏳ **Then:** Test the system with a real message
6. ⏳ **Then:** Enable RLS policies
7. ⏳ **Finally:** Research and decide on the 5 unclear tables
##

## Questions to Answer

1. **glyph_trail** - Is this for future analytics? Can it be deleted?
2. **messages** - Is this different from conversation_messages? Legacy?
3. **ritual_triggers** - Future feature or can be deleted?
4. **rupture_named** - Special glyph category or legacy?
5. **symbolic_interpreter** - Future feature or can be deleted?
