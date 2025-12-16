# User preferences DB migration

This folder contains a small SQL migration to create a server-side table used for storing simple UI
preferences (currently used to persist the "Save my chats" toggle).

Table: `user_preferences`

Columns:

- `user_id` (text) — primary key, maps to application user id
- `persist_history` (boolean) — whether to save chat history
- `persist_confirmed` (boolean) — whether the user explicitly consented
- `updated_at` (timestamptz) — last updated timestamp

To apply this migration to your Supabase/Postgres database, run (example):

```bash

# If you have psql configured with appropriate connection string / env var:
psql $DATABASE_URL -f sql/create_user_preferences_table.sql

# Or using the Supabase CLI (if authenticated):
supabase db remote set $YOUR_DB_CONNECTION_URL
psql $YOUR_DB_CONNECTION_URL -f sql/create_user_preferences_table.sql
```

Notes:

- This migration is intentionally minimal. If you prefer, create the table via
Supabase SQL editor in the web console.
- The `ConversationManager` implements best-effort REST upsert via the
  `/rest/v1/user_preferences` endpoint. Ensure proper Row Level Security (RLS)
and policies are set if you wish to allow authenticated clients to write.
