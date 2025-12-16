# Saoriverse Console Development Guide

## 🎯 Active Development Stack

The main application consists of these key files:

1. **Main Entry Point**
   - `main_v2.py` (root directory)

2. **Core Modules** (under `emotional_os/deploy/modules/`)
   - `ui.py` - Core UI rendering and logic
   - `auth.py` - Authentication system
   - Other supporting modules

## 🚫 Deprecated/Archived Files

Previous versions of the UI have been moved to the `deprecated/` directory:

- `emotional_os_ui.py (ARCHIVED)` (ARCHIVED) (old version)
- `main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py)` (ARCHIVED) (old version)

Additional archived files exist in:

- `emotional_os/archive/`
- `src/ui/` (retired stubs)
- `archive/previous_uis/`

⚠️ Do not modify or reference deprecated files. All new development should target the active stack.

## 🏃‍♂️ Running the Application

```bash

# Activate virtual environment (if using one)
source .venv/bin/activate

# Run the main application
streamlit run main_v2.py
```



## 💡 Development Guidelines

1. **Entry Point**: Always use `main_v2.py` as the application entry point
2. **UI Changes**: Make UI modifications in `emotional_os/deploy/modules/ui.py`
3. **Testing**: Test changes by running through `main_v2.py`
4. **Documentation**: Update this guide when making architectural changes

## Local preprocessor sample taxonomy and tests

We include a conservative sample taxonomy used by the local preprocessor for development and unit tests:

- `local_inference/emotional_taxonomy_sample.json`, contains a small set of canonical tags and embedded `escalation_tiers` used by tests.

Public audit API:

- `local_inference.preprocessor.Preprocessor.record_audit(payload)`, write a minimal audit entry. The audit entry will include `kind: preprocessor_audit`, the provided payload under `payload`, `taxonomy_source`, and `test_mode`.

How to run tests:

```bash

# activate the virtualenv in the project root (if present)
source .venv/bin/activate
pip install -r requirements.txt  # ensure test deps available
pytest -q
```



The tests added here exercise escalation logic and ensure `record_audit` writes a minimal log entry. When you provide the canonical `emotional_taxonomy.json` we can update the taxonomy and expand tests to match the editorial schema.

## CI badge

Fast preprocessor test feedback is available via GitHub Actions. Add the following badge to your repository README (or keep it here) to show the latest status for the focused preprocessor workflow:

```
![Preprocessor tests](https://github.com/taurinrobinson-wq/saoriverse-console/actions/workflows/preprocessor-tests.yml/badge.svg)
```



Note: the badge will display correctly once the workflow has run at least once on the repository (e.g., after a PR or a push). The workflow is configured to run on pull requests and executes only `tests/test_preprocessor.py` for fast feedback.
