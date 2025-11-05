# 🚀 Enable RLS - Step-by-Step Guide

## Status: RLS Not Yet Enabled ❌

Your conversations table is currently **unrestricted**. Follow these steps to lock it down.

---

## Option 1: Automatic (Easiest) ⭐ RECOMMENDED

### Step 1: Get the SQL

The complete RLS SQL is ready in your repo:

**File**: `sql/conversations_rls_policies.sql`

```bash
# View the file
cat sql/conversations_rls_policies.sql
```

### Step 2: Run in Supabase

1. **Open Supabase Dashboard**
   - URL: https://app.supabase.com/project/gyqzyuvuuyfjxnramkfq/sql/new

2. **Click "SQL Editor"** in left sidebar

3. **Click "New Query"** (+ button at top)

4. **Copy & Paste This SQL**

```sql
-- Enable RLS on conversations table
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;

-- Enable RLS on conversation_metadata table
ALTER TABLE public.conversation_metadata ENABLE ROW LEVEL SECURITY;

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

-- Policy 1: Users can SELECT their own conversation metadata
CREATE POLICY "Users can select own metadata"
ON public.conversation_metadata
FOR SELECT
USING (auth.uid()::text = user_id);

-- Policy 2: Users can INSERT their own conversation metadata
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
```

5. **Click "Run"** (Play button at top right)

6. **Wait for Success**
   - You should see: `Success - no rows returned` multiple times
   - This means all 8 policies were created! ✅

### Step 3: Verify RLS is Enabled

1. **Go to Authentication → Policies**
   - URL: https://app.supabase.com/project/gyqzyuvuuyfjxnramkfq/auth/policies

2. **Look for "conversations" table**
   - Should see 4 policies listed

3. **Look for "conversation_metadata" table**
   - Should see 4 more policies

**Total: 8 policies** ✅

---

## Option 2: Copy-Paste Entire File

If you prefer, just copy the entire file:

1. **Open file**: `sql/conversations_rls_policies.sql`

2. **Copy all contents** (Ctrl+A, Ctrl+C)

3. **Go to Supabase SQL Editor**
   - https://app.supabase.com/project/gyqzyuvuuyfjxnramkfq/sql/new

4. **Click New Query**

5. **Paste contents** (Ctrl+V)

6. **Click Run**

7. **Done!** All policies created ✅

---

## What Gets Created

| Component | Count | Purpose |
|-----------|-------|---------|
| **conversations** RLS | ✅ Enabled | Restricts table |
| **conversations** policies | 4 | SELECT, INSERT, UPDATE, DELETE |
| **conversation_metadata** RLS | ✅ Enabled | Restricts metadata table |
| **conversation_metadata** policies | 4 | SELECT, INSERT, UPDATE, DELETE |
| **Total** | **8 policies** | Full security |

---

## After Setup

### Test It Works

```python
# As User A, run this in your app:
conversations = manager.load_conversations()
# Result: Only User A's conversations

# Switch to User B:
conversations = manager.load_conversations()
# Result: Only User B's conversations (not User A's!)
```

### Expected Behavior

✅ **User A** sees only User A's conversations  
✅ **User B** sees only User B's conversations  
✅ **User A** cannot modify User B's data  
✅ **User B** cannot delete User A's conversations  

---

## ⚠️ Important Notes

1. **RLS must be enabled** before policies take effect
2. **Policies restrict anon key** (good for users)
3. **Service role key bypasses RLS** (admin access)
4. **Database enforces** - can't bypass from app
5. **Performance** - negligible impact

---

## Troubleshooting

### "Policy already exists" error?
- This means RLS is already enabled! Good! ✅
- Just means the script ran before
- Safe to run again

### "Still seeing all conversations"?
- Make sure you refreshed your app
- Check you're using **anon key** (not service role)
- Verify policies in Authentication → Policies

### "Getting permission denied"?
- This means RLS IS working! ✅
- Check your user_id matches auth.uid()
- See RLS_SETUP_GUIDE.md for troubleshooting

---

## Next Steps

1. ✅ Copy the SQL above
2. ✅ Paste into Supabase SQL Editor
3. ✅ Click "Run"
4. ✅ Check Authentication → Policies
5. ✅ See 8 policies listed
6. ✅ Restart your app
7. ✅ Test with multiple users

**You're done! RLS is now active.** 🔐

For questions, see:
- `RLS_SETUP_GUIDE.md` - Complete guide
- `RLS_QUICK_REFERENCE.md` - Quick reference
