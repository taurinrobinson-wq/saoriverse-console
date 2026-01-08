# Secret-scan and allowlist (detect-secrets)

This repository enforces secret scanning both locally (via `pre-commit`) and in CI (GitHub Actions) using `detect-secrets`.

What we added

- `.pre-commit-config.yaml`, runs `detect-secrets` and basic hygiene hooks locally.
- `.github/workflows/secret_scan.yml`, runs `detect-secrets scan --all-files` in CI and fails the run if new secrets are detected.
- `.secret-allowlist`, a list of fnmatch-style globs for files that the CI will ignore (useful for example/template files).

Why we have an allowlist

- Some projects keep template files (for example `.env.example`, `.toml.template`, etc.) in the repo. Those files may contain placeholder-looking values which can produce false positives. The allowlist lets you explicitly permit specific paths/patterns while still protecting the rest of the repository.

How to update the allowlist

1. Edit `.secret-allowlist` in the repository root.
2. Add one glob per line (fnmatch style). Example:

```
*.env.example
deploy/*.toml
templates/*.template
```


3. Commit and push. CI will respect the allowlist when deciding whether a push/PR should fail.

Security best practices

- Do not commit real secrets (API keys, OAuth tokens, private keys) to the repository.
- Use environment variables and GitHub Secrets for runtime configuration.
- If a credential is accidentally committed, rotate/revoke it immediately (see rotation steps below).

Rotation / revocation steps (high-level)

1. Identify the provider (e.g., OpenAI, Google Cloud, OAuth provider).
2. Log in to the provider console and revoke or rotate the key/token.
3. Update the environment where the app runs to use the new credential (e.g., GitHub Secrets, server env vars).
4. If the secret was committed and pushed, remove it from history (we already scrubbed `deploy/CoPilot_chunks`) and force-pushed the cleaned branch. Notify collaborators, they must reset to the rewritten `main` (see below).

How collaborators can sync after a history rewrite
If the main branch was force-pushed after a scrub, instruct collaborators to do the following:

```bash

# Fetch and reset local main to match origin
git fetch origin
git checkout main
git reset --hard origin/main

# Optional: clean reflog and run garbage collection
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```


Optional enhancements I can add

- A strict baseline for `detect-secrets` to reduce noisy findings.
- A stricter allowlist policy (require a comment marker inside allowed files).
- A small README section showing common false positives and how to address them.

If you'd like any of the above additions, tell me which one and I will implement it.
