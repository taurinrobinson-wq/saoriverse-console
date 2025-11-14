Deployment checklist — migrate conversations to row-per-message and enable RLS

Preflight (local/staging):

1. Backup
   - Take a snapshot/backup of the Supabase DB (project settings -> Backups) or pg_dump.
   - Confirm backup completes and store the snapshot ID.

2. Verify user_id format
   - Run the pre-check SQL from `sql/conversations_migrate_to_uuid_20251108.sql` in staging and ensure it returns zero rows:
     SELECT user_id
     FROM public.conversations
     WHERE user_id IS NOT NULL
       AND NOT (user_id ~* '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$');

3. Run migration in staging
   - Execute `sql/conversations_migrate_to_uuid_20251108.sql` in Supabase SQL editor.
   - Verify `conversations_backup_20251108` exists and row counts match.

4. Create messages table and policies
   - Execute `sql/create_conversation_messages.sql`.
   - Confirm `conversation_messages` table exists and RLS is enabled.

5. Deploy updated edge function
   - Deploy `emotional_os/deploy/saori_edge_function.ts` to your Functions/Edge environment.
   - Ensure env vars `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and `OPENAI_API_KEY` are set in the deployment environment.

6. Frontend patch
   - The static frontend at `emotional_os/static/index.html` has been patched to load conversations from `conversation_messages`, group by `conversation_id`, and add per-thread CSV export.
   - Deploy or serve the patched frontend.

Verification (staging):

1. Authenticated session test
   - Sign in with a test user.
   - Send a message. Confirm two rows are created in `conversation_messages` (user + assistant) with the same `conversation_id` and timestamptz values in ISO format.
   - Check `conversations` metadata row is present and `message_count` matches the number of rows in `conversation_messages` for that conversation.

2. RLS test
   - Using the anon/regular client (logged in as the test user), run a SELECT for `conversation_messages` and confirm you only see rows where `user_id = auth.uid()`.
   - Validate that a different test user cannot access the first user's messages.

3. CSV export
   - Use the UI export button on a conversation thread. Confirm the downloaded CSV contains headers: UID, First Name, Role, Timestamp, Message with ISO timestamps.

Rollback plan

- If migration fails or data is inconsistent, use `public.conversations_backup_20251108` to restore data.
  - Option A (fast swap): Rename current table and rename backup into place (requires care if downstream FKs exist).
  - Option B: TRUNCATE and re-insert from backup.
- If RLS policies cause access issues, drop the newly-created policies and revert to previous policy definitions using saved SQL.

Notes & reminders

- Rotate any leaked keys found in the repo before deploying to production.
- Run the migration in a staging environment first and test thoroughly.
- Keep the backup table for a retention period (e.g., 7 days) until confident.

Contact me if you want me to create a one-click Supabase Assistant message that runs the migration and returns verification output.