Title: chore(ci): focused preprocessor tests + taxonomy validator

Body:
This PR adds a lightweight CI workflow focused on the local preprocessor unit tests and
a taxonomy validator intended to protect the canonical emotional taxonomy JSON.

What it does:
- Adds `.github/workflows/preprocessor-tests.yml` which runs on pull requests and executes:
  - `pytest -q tests/test_preprocessor.py` (fast, focused unit tests)
  - `pytest -q tests/test_taxonomy_validator.py` (validator; skipped unless `local_inference/emotional_taxonomy.json` is present)

Why:
- Provides fast feedback for the preprocessor module during development without running the full integration/perf suites.
- Ensures any canonical taxonomy added in a PR conforms to the editorial schema via an automated validator.

Notes:
- The taxonomy validator is skip-on-missing so it won't fail existing PRs until a canonical taxonomy is added.
- If you'd like me to update the PR description on GitHub I can do so with an authenticated GitHub API/CLI session; instead I added this file to the branch so you can copy/paste it into the PR body quickly.

How to use:
- Review the changes in this branch and paste the content of this file into the PR body when creating the PR (or paste only selected parts).
