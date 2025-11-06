Title: merge(feature/preprocessor-ci): preprocessor prefs, responsive header, dark theme fixes, tests & CI

Body:
This merge brings together a group of focused improvements to the local preprocessor, UI responsiveness, accessibility in dark mode, and the developer testing/CI workflow.

Key updates
- Preprocessor preferences
  - Added server-backed preference helpers to `ConversationManager`:
    - `load_user_preferences()` and `save_user_preferences()`
  - UI wired to persist the "Save my chats" toggle (best-effort) and to load saved preferences on startup when a `ConversationManager` is available.
- Responsive header and branding
  - Reworked the app header to a single responsive `brand-row` (flexbox) so the logo and `FirstPerson - Personal AI Companion` title align horizontally on wide screens and stack gracefully on small screens.
  - Added matching styles for light and dark themes (`emotional_os_ui.css`, `emotional_os_ui_light.css`, `emotional_os_ui_dark.css`).
- Dark theme fixes
  - Improved contrast for ghost/secondary buttons (e.g., Logout) and file uploader labels to ensure readability in dark mode.
- Tests & CI
  - Added `tests/test_user_preferences.py` (mocked requests) to validate preference load/save helpers.
  - Updated `.github/workflows/preprocessor-tests.yml` to run the prefs tests alongside existing focused preprocessor tests and the taxonomy validator.
- DB migration
  - Added a minimal SQL migration `sql/create_user_preferences_table.sql` and `sql/README.md` describing how to apply it (creates `user_preferences` table used by the REST upsert).

Verification performed
- Local pytest run for the new prefs tests (mocked) — passed.
- Local syntax checks and a successful local merge into `main` with `git`.

Notes & follow-ups
- The preference persistence is best-effort: falls back to session-only behavior if Supabase / network is unavailable or the user is anonymous.
- If you want cross-device persistence for anonymous users, consider an anonymous-id approach or a small client-side cookie/localStorage fallback (held off per request).
- The SQL migration expects a `user_preferences` table accessible via the Supabase REST endpoint `/rest/v1/user_preferences` (ensure RLS/policies if writing from clients).

If desired, copy this body into the PR description or the release notes to preserve lineage and audit history.
