# 🔐 Row Level Security (RLS) Setup Guide

## Overview

Your conversations table is currently **unrestricted**. Anyone with database access can read all users' conversations! This guide walks you through enabling RLS to lock it down.

## What is RLS?

**Row Level Security** restricts database access at the row level:
- ✅ User A can only see User A's conversations
- ✅ User B can only see User B's conversations
- ❌ Users cannot see each other's data
- ❌ Attackers cannot bulk export all conversations

## Setup (2 Steps)

### Step 1: Enable RLS on Tables

```sql
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_metadata ENABLE ROW LEVEL SECURITY;
```

### Step 2: Create Security Policies

Run the companion SQL file: `sql/conversations_rls_policies.sql`

**Via Supabase Dashboard:**
1. Go to SQL Editor
2. Create new query
3. Copy entire contents of `sql/conversations_rls_policies.sql`
4. Click "Run"

**What gets created:**
- SELECT policy: Users can only query their own data
- INSERT policy: Users can only create their own data
- UPDATE policy: Users can only modify their own data
- DELETE policy: Users can only delete their own data

## The Policies (What Gets Protected)

### SELECT Policy
```sql
CREATE POLICY "Users can select own conversations"
ON public.conversations
FOR SELECT
USING (auth.uid()::text = user_id);
```
**Effect**: `SELECT * FROM conversations` returns ONLY rows where `user_id = current_user_id`

### INSERT Policy
```sql
CREATE POLICY "Users can insert own conversations"
ON public.conversations
FOR INSERT
WITH CHECK (auth.uid()::text = user_id);
```
**Effect**: Users can only INSERT if they set `user_id` to their own `auth.uid()`

### UPDATE Policy
```sql
CREATE POLICY "Users can update own conversations"
ON public.conversations
FOR UPDATE
USING (auth.uid()::text = user_id)
WITH CHECK (auth.uid()::text = user_id);
```
**Effect**: Users can only UPDATE their own rows

### DELETE Policy
```sql
CREATE POLICY "Users can delete own conversations"
ON public.conversations
FOR DELETE
USING (auth.uid()::text = user_id);
```
**Effect**: Users can only DELETE their own rows

## Which API Key is Used?

| Key Type | RLS Enforced | Use Case |
|----------|--------------|----------|
| **Anon Key** | ✅ YES | Client app (users) |
| **Service Role Key** | ❌ NO | Backend/admin (bypasses RLS) |

**In your app**: Use the **anon key** so RLS is enforced for users

**For admin operations**: Use **service role key** to bypass RLS (careful!)

## Verification

To check RLS is enabled, run in SQL Editor:

```sql
-- Check RLS status
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('conversations', 'conversation_metadata');

-- Check policies
SELECT tablename, policyname, qual, with_check 
FROM pg_policies 
WHERE tablename IN ('conversations', 'conversation_metadata')
ORDER BY tablename, policyname;
```

**Expected output:**
```
rowsecurity = true for both tables
4 policies per table (select, insert, update, delete)
```

## Testing RLS

### Test 1: As User A

```sql
-- Login as User A (auth.uid() = 'user-a-uuid')
SELECT * FROM conversations;
-- Result: Only User A's conversations
```

### Test 2: As User B

```sql
-- Login as User B (auth.uid() = 'user-b-uuid')
SELECT * FROM conversations;
-- Result: Only User B's conversations, cannot see User A's
```

### Test 3: Bypass with Service Role

```sql
-- Using service role key (admin access)
SELECT * FROM conversations;
-- Result: ALL conversations (RLS bypassed)
```

## Important Notes

### For Supabase Auth Users

If you're using **Supabase Auth** (recommended):
- ✅ `auth.uid()` returns authenticated user's ID
- ✅ RLS policies work automatically
- ✅ Very secure out-of-the-box

### For Custom Authentication

If you're using **custom auth** (not Supabase Auth):

**Problem**: The policies use `auth.uid()` which won't work with custom auth

**Solution**: Modify the policies to use your auth method:

```sql
-- Example: If you use a 'current_user_id' setting
CREATE POLICY "Users can select own conversations"
ON public.conversations
FOR SELECT
USING (user_id = current_setting('app.current_user_id'));

-- Then set the value before queries:
-- SET app.current_user_id = 'user-123';
```

Or update the `user_id` column before INSERT:

```python
# In your Python app
import os
current_user = os.getenv('CURRENT_USER_ID')

# When inserting, set user_id automatically
payload = {
    'user_id': current_user,  # ← Set automatically
    'conversation_id': conv_id,
    'title': title,
    'messages': messages
}
```

## Current Implementation Status

### In Your App

Your `conversation_manager.py` stores `user_id` from the session:

```python
class ConversationManager:
    def __init__(self, user_id: str, ...):
        self.user_id = user_id  # User's ID
```

### What Needs to Match

For RLS to work, the `user_id` in your payload **must match** `auth.uid()`:

```python
# This works with RLS:
payload = {
    'user_id': auth.uid(),           # ✅ Matches auth
    'conversation_id': conv_id,
    'messages': messages
}

# This doesn't:
payload = {
    'user_id': 'hardcoded-id',       # ❌ Doesn't match auth
    'conversation_id': conv_id,
    'messages': messages
}
```

## Quick Reference

### Enable RLS (2 steps)

```bash
# 1. Run this in Supabase SQL Editor
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_metadata ENABLE ROW LEVEL SECURITY;

# 2. Then run sql/conversations_rls_policies.sql
# (Copy entire file, paste in SQL editor, click Run)
```

### Verify RLS is Active

```bash
# Check in Supabase Dashboard:
# Authentication → Policies
# Should show policies for conversations table
```

### Test Access

```bash
# As a user, try:
SELECT COUNT(*) FROM conversations;
# Result: Should see only YOUR conversations

# Try accessing someone else's:
SELECT * FROM conversations WHERE user_id = 'other-user-id';
# Result: Empty (RLS blocks it)
```

## Security Comparison

### Before RLS (Current - INSECURE ❌)
```
Any authenticated user can:
  - SELECT all conversations (all users)
  - UPDATE all conversations
  - DELETE all conversations
  
Privacy: None
```

### After RLS (Recommended - SECURE ✅)
```
Each user can only:
  - SELECT their own conversations
  - UPDATE their own conversations
  - DELETE their own conversations
  
Privacy: Perfect (enforced at DB level)
```

## Best Practices

1. ✅ **Always enable RLS** on user-scoped tables
2. ✅ **Use anon key** in client apps (enforces RLS)
3. ✅ **Use service key** only for admin operations
4. ✅ **Test RLS** with multiple user accounts
5. ✅ **Monitor policies** in Supabase dashboard
6. ❌ **Never disable RLS** in production
7. ❌ **Never hardcode user IDs** - let `auth.uid()` handle it

## Common Issues

### "User cannot insert into conversations"

**Cause**: RLS policy not set correctly

**Fix**:
```sql
-- Make sure INSERT policy allows:
CREATE POLICY "Users can insert own conversations"
ON public.conversations
FOR INSERT
WITH CHECK (auth.uid()::text = user_id);
```

### "Can see all conversations"

**Cause**: RLS not enabled

**Fix**:
```sql
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
```

### "Queries return empty"

**Cause**: Wrong user_id or auth not working

**Fix**:
1. Check `auth.uid()` returns a value: `SELECT auth.uid();`
2. Check user_id matches: `SELECT user_id, COUNT(*) FROM conversations GROUP BY user_id;`
3. Verify policy: `SELECT * FROM pg_policies WHERE tablename = 'conversations';`

## Next Steps

1. ✅ Run `sql/conversations_rls_policies.sql` in Supabase
2. ✅ Verify policies in Authentication → Policies
3. ✅ Test with multiple user accounts
4. ✅ Monitor in Supabase dashboard
5. ✅ Sleep well knowing your data is secure! 😴

## References

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL RLS Docs](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Your SQL policies file](conversations_rls_policies.sql)

---

**Remember**: RLS is database-level security. Even if someone compromises your app, they can't access other users' data! 🔐
