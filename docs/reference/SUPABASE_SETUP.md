# ⚙️ Supabase Setup Guide - Conversation Storage

Your Supabase credentials are now configured! Follow these steps to enable persistent conversation storage.

## Step 1: Create Database Tables

The SQL schema needs to be created in your Supabase database.

### Option A: Automatic Setup (Recommended)

If you have `supabase-cli` installed:

```bash
cd /workspaces/saoriverse-console
```text
```text
```



### Option B: Manual Setup via Supabase Dashboard

1. **Go to Supabase Dashboard**
   - URL: https://app.supabase.com/project/gyqzyuvuuyfjxnramkfq/sql/new

2. **Create New Query**
   - Click "SQL Editor" in the left sidebar
   - Click "New Query" (+ button)

3. **Copy & Paste SQL**
   - Copy the entire SQL from below OR from `sql/conversations_table.sql`
   - Paste into the SQL editor

4. **Run the Query**
   - Click the "Run" button (play icon)
   - You should see "Success" message
##

## SQL Schema (Paste into Supabase SQL Editor)

```sql

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

```text
```



##

## Step 2: Verify Installation

After running the SQL, verify the tables were created:

```bash
cd /workspaces/saoriverse-console
```text
```text
```



You should see:

```

✅ conversations table EXISTS
✅ conversation_metadata table EXISTS

```text
```



##

## Step 4: Enable Row Level Security (RLS) ⚠️ IMPORTANT FOR SECURITY

**This step secures your conversations table so users can only access their own data.**

### Enable RLS

1. Go to Supabase Dashboard → SQL Editor
2. Create new query
3. Run this SQL:

```sql
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
```text
```text
```



You should see: `Success - no rows returned`

### Add RLS Policies

1. Create another new query
2. Copy entire contents of `sql/conversations_rls_policies.sql`
3. Paste into SQL editor
4. Click "Run"

You should see multiple `Success` messages (one per policy)

### Verify RLS is Active

Check Authentication → Policies in Supabase dashboard

You should see policies for:
- `conversations` table (4 policies)
- `conversation_metadata` table (4 policies)

✅ **RLS is now active!** Users can only access their own conversations.
##

## Step 5: Configure Streamlit Secrets (Already Done ✅)

Your `.streamlit/secrets.toml` is already configured with:

```toml

[supabase]
url = "https://gyqzyuvuuyfjxnramkfq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXp5dXZ1dXlmanhucmFta2ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NjcyMDAsImV4cCI6MjA3MTA0MzIwMH0.4SpC34q7lcURBX4hujkTGqICdSM6ZWASCENnRs5rkS8"
service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXp5dXZ1dXlmanhucmFta2ZxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2NzIwMCwiZXhwIjoyMDcxMDQzMjAwfQ.sILcK31ECwM0IUECL0NklBdv4WREIxToqtCdsMYKWqo"
auth_function_url = "https://gyqzyuvuuyfjxnramkfq.supabase.co/functions/v1/auth-manager"
saori_function_url = "https://gyqzyuvuuyfjxnramkfq.supabase.co/functions/v1/authenticated-saori"

```text
```




✅ **No changes needed** - everything is ready!
##

## Step 6: Restart Your App

```bash
```text
```text
```



You should now see:
- ✅ Sidebar with "Previous Conversations"
- ✅ "💾 Save my chats" toggle
- ✅ Conversations auto-save when you check the toggle
- ✅ Data persists across page refreshes!
##

## Troubleshooting

### Tables not appearing in Supabase

1. **Check you clicked "Run" button** - The SQL must be executed
2. **Look for error messages** - If there's a red error, check the syntax
3. **Verify credentials** - Make sure you're in the right project
4. **Try again** - Sometimes Supabase has temporary issues

### App not saving conversations

1. **Check toggle** - Make sure "💾 Save my chats" is checked
2. **Check credentials** - Verify `.streamlit/secrets.toml` has correct URL/key
3. **Check database** - Use Supabase dashboard to see if data appears
4. **Check logs** - Look for error messages in terminal

### Error: "conversations table not found"

Run the migration script again:

```bash

python3 scripts/migrate_supabase.py --verify

```



If it says tables don't exist, go back to Step 1 and run the SQL.
##

## Testing the Setup

### Test 1: Create a Conversation

1. Open the app: `streamlit run app.py`
2. Log in with a test account
3. Check "💾 Save my chats"
4. Send a message
5. Go to Supabase Dashboard → "conversations" table
6. Should see 1 new row!

### Test 2: Persistence

1. Send another message in the same conversation
2. Refresh browser (F5)
3. Your conversation should be there!
4. Previous message should still be visible in sidebar

### Test 3: Rename

1. In sidebar, click ✏️ next to conversation
2. Type new name
3. Click "Save"
4. Name should update immediately
5. Refresh browser - new name persists!
##

## Next Steps

Now that the database is set up:

1. ✅ **Database schema created**
2. ⏳ **Start using the app** - conversations will auto-save
3. ⏳ **Monitor Supabase dashboard** - see data flowing in
4. ⏳ **Test all features** - sidebar, rename, delete
##

## Files & Documentation

- **`sql/conversations_table.sql`** - Database schema
- **`emotional_os/deploy/modules/conversation_manager.py`** - Python API
- **`CONVERSATION_STORAGE.md`** - Complete documentation
- **`QUICKSTART_CONVERSATION_STORAGE.md`** - Quick start guide
- **`scripts/migrate_supabase.py`** - Migration helper script
##

## Need Help?

- Check logs: Look for errors in terminal
- Verify tables: `python3 scripts/migrate_supabase.py --verify`
- Review docs: See `CONVERSATION_STORAGE.md`
- Check Supabase: Use dashboard to inspect data

**You're all set! Conversations will now persist. 🎉**
