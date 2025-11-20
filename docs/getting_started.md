# Getting Started

This short guide helps new contributors get up and running safely in the Saoriverse Console.

Prereqs

- Python 3.11+ and pip
- Optional: Deno for local edge-function testing

Quick steps

1. Clone the repository

```bash
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console
```

2. Load safe defaults

```bash
cp .env.template .env  # Load safe defaults for local-only mode
```

3. (Optional) Install Python deps

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt      # runtime deps
pip install -r requirements-dev.txt  # dev/test deps
```

4. Run the enrichment pipeline (example)

```bash
python3 enrich_runner.py
```

5. View logs

```bash
tail -f logs/enrich.log
```

6. Run tests

```bash
pytest -q
```

Makefile (quick shortcuts)

You can use the included `Makefile` to run common developer rituals:

```bash
make env        # Load safe defaults
make install    # Create virtualenv and install deps
make enrich     # Run the enrichment pipeline
make test       # Run tests
make logs       # View recent enrichment logs
```

Processing modes

- `local` — Fully offline. Default. No remote AI calls allowed.
- `hybrid` — Enables remote AI (OpenAI, Supabase hybrid processors).
- `premium` — Optional tier for advanced generation tasks.

Opt-in for remote AI
--------------------

To enable remote AI calls for testing or trusted environments:

```bash
export PROCESSING_MODE=hybrid
export ALLOW_REMOTE_AI=1
```

CI & guard enforcement

- A GitHub Actions workflow runs `pytest` on push and pull requests to `main`.
- Runtime guards are in place:
  - Python factory functions will raise a `RuntimeError` when explicit remote config is provided in `local` mode.
  - Edge functions return HTTP 403 when remote AI is disabled.

Notes

- `.env.template` is tracked as a safe onboarding artifact (contains no secrets). Do not store secrets in the repository; use your deployment platform's secret management for keys like `OPENAI_API_KEY` or `SUPABASE_SERVICE_ROLE_KEY`.

If you want, I can also add this getting-started pointer to the root `README.md`.
