# Emotion Learning System - Supabase Setup Guide

## Overview
This guide walks you through setting up the privacy-first emotion learning system in Supabase. The system consists of two tables:

1. **emotions_log** - Stores emotion metadata detected by the browser
2. **emotion_thresholds** - Stores per-user adaptive thresholds calculated by the training script

## Prerequisites
- Access to your Supabase project dashboard
- Service role key (for backend operations)

---

## Step 1: Create the `emotions_log` Table

This table stores emotion detection metadata. **No images, videos, or biometric data** — only emotion labels and confidence scores.

### SQL to create the table:

```sql
-- Create emotions_log table
create table if not exists public.emotions_log (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  emotion text not null,
  confidence float8 not null check (confidence >= 0 and confidence <= 1),
  timestamp timestamptz not null default now(),
  conversation_context text default 'default',
  created_at timestamptz default now()
);

-- Create index for faster queries by user and time
create index if not exists emotions_log_user_time_idx
  on public.emotions_log (user_id, timestamp desc);

-- Create index for conversation context queries
create index if not exists emotions_log_context_idx
  on public.emotions_log (user_id, conversation_context, timestamp desc);
```

### How to apply:
1. Go to **SQL Editor** in Supabase Dashboard
2. Click **New Query**
3. Paste the SQL above
4. Click **Run**
5. You should see: `Success. No rows returned`

---

## Step 2: Create the `emotion_thresholds` Table

This table stores per-user emotion detection thresholds calculated by `train_emotion_model.py`.

### SQL to create the table:

```sql
-- Create emotion_thresholds table
create table if not exists public.emotion_thresholds (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  emotion text not null,
  threshold float8 not null check (threshold >= 0 and threshold <= 1),
  updated_at timestamptz not null default now(),
  unique(user_id, emotion)
);

-- Create index for faster lookups
create index if not exists emotion_thresholds_user_idx
  on public.emotion_thresholds (user_id);
```

### How to apply:
1. Go to **SQL Editor** in Supabase Dashboard
2. Click **New Query**
3. Paste the SQL above
4. Click **Run**
5. You should see: `Success. No rows returned`

---

## Step 3: Enable Realtime on `emotion_thresholds`

The frontend EmotionDetector component uses Supabase Realtime to automatically update thresholds when the training script modifies them.

### How to enable:
1. Go to **Table Editor** in Supabase Dashboard
2. Click on **emotion_thresholds** table
3. Click **Realtime** button in the top right
4. Enable the following events:
   - ✓ INSERT
   - ✓ UPDATE
   - ✓ DELETE

---

## Step 4: Set Up Row Level Security (Optional but Recommended)

Restrict access so users can only see their own data:

```sql
-- Enable RLS on emotions_log
alter table public.emotions_log enable row level security;

-- Create policy: authenticated users can insert their own emotion data
create policy "Users can insert own emotion logs"
  on public.emotions_log for insert
  with check (
    auth.uid()::text = user_id
  );

-- Create policy: authenticated users can view their own emotion logs
create policy "Users can view own emotion logs"
  on public.emotions_log for select
  with check (
    auth.uid()::text = user_id
  );

-- Enable RLS on emotion_thresholds
alter table public.emotion_thresholds enable row level security;

-- Create policy: authenticated users can view their own thresholds
create policy "Users can view own emotion thresholds"
  on public.emotion_thresholds for select
  with check (
    auth.uid()::text = user_id
  );
```

**Note:** If you're not using Supabase Auth, you can skip this section and manage access at the API layer.

---

## Step 5: Verify Tables Were Created

1. Go to **Table Editor** in Supabase Dashboard
2. You should see both tables in the left sidebar:
   - `emotions_log` (with columns: id, user_id, emotion, confidence, timestamp, conversation_context, created_at)
   - `emotion_thresholds` (with columns: id, user_id, emotion, threshold, updated_at)

---

## Step 6: Configure Environment Variables

Ensure your backend has these environment variables set:

```bash
# .env.local (Next.js)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # Keep private!

# For train_emotion_model.py
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

---

## Workflow Summary

### Frontend (EmotionDetector.tsx)
1. Detects emotion using face-api.js (browser-side, no video transmission)
2. Fetches thresholds from `/api/emotion-thresholds` via GET request
3. Subscribes to Supabase Realtime for threshold updates
4. Only sends emotion metadata to `/api/emotions` if confidence ≥ threshold
5. Payload: `{emotion, confidence, timestamp, user_id, conversation_context}`

### Backend (Next.js API Routes)
1. `/api/emotions` (POST): Receives emotion metadata, validates, stores in `emotions_log`
2. `/api/emotions` (GET): Retrieves recent emotion logs for a user
3. `/api/emotion-thresholds` (GET): Fetches user's thresholds for frontend
4. `/api/emotion-thresholds` (POST): Updates thresholds (called by training script)

### Training Script (train_emotion_model.py)
1. Queries `emotions_log` for a user over N days
2. Analyzes emotion patterns: frequency and average confidence
3. Calculates adaptive thresholds: lower for frequently detected emotions, higher for rare ones
4. Updates `emotion_thresholds` table via `/api/emotion-thresholds` or direct Supabase insert
5. Frontend automatically receives updates via Realtime

---

## Testing the System

### Test 1: Manually insert emotion data
```sql
insert into public.emotions_log (user_id, emotion, confidence, conversation_context)
values ('test_user_123', 'sad', 0.85, 'grief_support');
```

### Test 2: Verify frontend can fetch thresholds
```bash
curl "http://localhost:3000/api/emotion-thresholds?user_id=test_user_123"
```

### Test 3: Run training script
```bash
python train_emotion_model.py --user_id test_user_123
```

---

## Monitoring and Optimization

### Check emotion logs by user:
```sql
select emotion, confidence, timestamp
from public.emotions_log
where user_id = 'your_user_id'
order by timestamp desc
limit 20;
```

### View user's thresholds:
```sql
select emotion, threshold, updated_at
from public.emotion_thresholds
where user_id = 'your_user_id'
order by emotion;
```

### Delete old logs (optional cleanup):
```sql
delete from public.emotions_log
where timestamp < now() - interval '90 days';
```

---

## Privacy & Security Notes

✓ **No video transmission** - Only emotion metadata leaves the browser
✓ **No biometric storage** - Only emotion labels and confidence scores
✓ **No conversation transcripts** - Optional context field for tagging
✓ **User-specific thresholds** - Each user gets personalized detection sensitivity
✓ **Row-level security** - (Optional) Restricts data access by authenticated user
✓ **Service role key** - Keep private; only expose anon key to frontend

---

## Troubleshooting

**Problem:** `Supabase insert error: 23505 unique violation`
**Solution:** Check if you're trying to insert duplicate (user_id, emotion) in emotion_thresholds. Use UPSERT instead.

**Problem:** `Column "threshold" does not exist`
**Solution:** Run the schema creation SQL from Step 2.

**Problem:** Frontend not receiving Realtime updates
**Solution:** Enable Realtime on emotion_thresholds table (Step 3) and ensure Realtime is active in Supabase project settings.

**Problem:** `SUPABASE_SERVICE_ROLE_KEY not found`
**Solution:** Set environment variables in `.env.local` or `export` before running train_emotion_model.py.

---

## Next Steps

1. ✓ Create tables in Supabase (Steps 1-2)
2. ✓ Enable Realtime (Step 3)
3. ✓ Configure environment variables (Step 6)
4. Run the frontend with EmotionDetector component
5. Periodically run `train_emotion_model.py` to refine thresholds
6. Monitor emotion logs in Supabase to understand user patterns
