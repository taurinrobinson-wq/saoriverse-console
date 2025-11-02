# Phase 2 — Integration Guide (Placeholder)

Quick integration notes for developers who want to connect the UI, extractor, and Supabase persistence.

Steps
1. Local dev: create and activate venv; install requirements from `requirements.txt`.
2. Run Streamlit UI: `streamlit run main_v2.py`.
3. To enable server persistence, set Supabase URL and anon/service_role in your secrets and opt-in via the UI.
4. Apply SQL DDL in `sql/create_conversation_history_tables.sql` using Supabase SQL editor or psql.

Notes
- Service-role key required to run DDL or administrative operations.
- RLS policies recommended; see `sql/rls_policies.sql`.

TODO
- Add code snippets for the REST POST used by UI to persist messages.
- Add example Supabase policies for `user_id` mapping.