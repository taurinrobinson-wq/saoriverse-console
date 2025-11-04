# 🔐 RLS Quick Reference Card

## What Is RLS?

**Row Level Security** = Database-enforced access control

- ✅ User A can only see User A's data
- ✅ Enforced by the database itself
- ✅ Can't be bypassed from the app
- ✅ Better than app-level security

## Quick Setup (3 Minutes)

### 1. Enable RLS
```sql
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_metadata ENABLE ROW LEVEL SECURITY;
```

### 2. Add Policies
```bash
# Copy entire contents of:
sql/conversations_rls_policies.sql
# Paste into Supabase SQL Editor
# Click "Run"
```

### 3. Verify
```bash
# Go to Supabase Dashboard
# Authentication → Policies
# Should see 8 policies (4 per table)
```

## The Policies (What They Do)

| Policy | Effect |
|--------|--------|
| **SELECT** | User sees only own conversations |
| **INSERT** | User creates only under their ID |
| **UPDATE** | User modifies only own data |
| **DELETE** | User deletes only own data |

## API Keys

| Key | RLS | Use Case |
|-----|-----|----------|
| **Anon** | ✅ Enforced | Your Streamlit app |
| **Service Role** | ❌ Bypassed | Admin/backend only |

## Files

| File | Purpose |
|------|---------|
| `sql/conversations_rls_policies.sql` | RLS policy SQL |
| `RLS_SETUP_GUIDE.md` | Detailed guide |
| `SUPABASE_SETUP.md` | Step 4: RLS setup |

## Verify It Works

### Command
```sql
-- This only shows YOUR conversations
SELECT * FROM conversations;

-- Try to peek at someone else's (fails)
SELECT * FROM conversations WHERE user_id = 'other-user-id';
-- Result: Empty (RLS blocks it)
```

### Visual Test
1. Login as User A → Send message
2. Logout, login as User B → Can't see User A's message ✅

## Common Issues

| Problem | Fix |
|---------|-----|
| "Can see all conversations" | RLS not enabled - run ALTER TABLE |
| "Can't insert conversations" | Policy blocked - check user_id matches auth |
| "Returns empty" | Wrong user_id or auth not working |

## Key Concept

```
WITHOUT RLS:
┌─────────────────────────────────┐
│ Supabase Database (OPEN!)       │
│ • All users' conversations      │
│ • Anyone can read/write         │
│ • No access control             │
└─────────────────────────────────┘

WITH RLS:
┌─────────────────────────────────┐
│ Supabase Database (LOCKED!)     │
│ ┌────────────┐ ┌────────────┐   │
│ │ User A     │ │ User B     │   │
│ │ conversations       conversations   │
│ │ (Access ✅)│ │ (Access ✅)│   │
│ └────────────┘ └────────────┘   │
│ Can't cross access              │
└─────────────────────────────────┘
```

## One-Liner

**RLS = Database says "Sorry, that's not your data" before your app even gets a chance to mess up.** 🔐

---

See **RLS_SETUP_GUIDE.md** for full documentation.
