# Dev Archive

This folder contains developer-oriented scripts and one-off utilities moved out of the main tree to
keep the repository tidy. Files in this folder are safe to restore with `git mv` if you need them
back.

## Test fallbacks

To make the test-suite safe for local development without a configured Supabase instance, the test
fixtures include conservative, non-destructive environment fallbacks. These defaults only apply when
the corresponding environment variables are not already set, so they will not override a real
integration configuration.

Key variables that the test fallbacks provide (only when missing):

- `SUPABASE_URL` — default: `http://localhost:8000`
- `SUPABASE_AUTH_URL` — built from `SUPABASE_URL` as `/functions/v1/auth-manager`
- `SUPABASE_FUNCTION_URL` — built from `SUPABASE_URL` as `/functions/v1`
- `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_ANON_KEY` — default: `test_platform_key`
- `TEST_CUSTOM_TOKEN` / `TEST_ACCESS_TOKEN` — default: `test_custom_token` / `test_access_token`
- `TEST_USER_ID` — default: `test_user`

## How to opt into real integration tests

If you want tests to exercise a real Supabase deployment (integration tests), set the real
environment variables before running tests (for example in a local `.env` or `env` file loaded by
your shell):

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_PUBLISHABLE_KEY="your-publishable-key"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export PROJECT_JWT_SECRET="your-jwt-secret"

# (optional) override other test vars
export TEST_CUSTOM_TOKEN="..."
```text
```text
```

When the real env vars are present, the tests will use them instead of the fallbacks and perform
real network calls against your Supabase instance.

## Restoring files

To restore a file to the main tree:

```bash

git mv dev_archive/<path> <original/path>
git commit -m "chore: restore <file> from dev_archive"

```
