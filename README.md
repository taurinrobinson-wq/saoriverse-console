# SaoriVerse Console - FirstPerson

A private, local-first emotional AI companion with integrated voice interface.

**Status**: Post-reorganization (Phase 9) - Clean, modular architecture
##

## Quick Start

### 1. Install Dependencies

```bash
```text
```



### 2. Run the Application

```bash
```text
```



Opens automatically in your browser at `http://localhost:8501`

### 3. (Optional) Enable Voice
Configure voice settings in the sidebar when running app.py
##

## 📂 Project Organization

This project uses a clean folder structure to prevent clutter:
- **`src/`** — Main source code
- **`scripts/`** — Development utilities (see `scripts/RUN_WEB_DEV.sh`)
- **`docs/`** — Intentional, curated documentation only
- **`scratch/`** — Auto-generated notes (not tracked in git)
- **`velinor/`** — Velinor game implementation (Streamlit)
- **`velinor-web/`** — Velinor web version (Next.js)

👉 **[See Full Structure Guide](./docs/PROJECT_STRUCTURE.md)**

## 🚀 Quick Commands

```bash

# Start Velinor web game (dev mode)
./scripts/RUN_WEB_DEV.sh

# Start full stack (frontend + backend)
./scripts/RUN_FULL_STACK.sh

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
```text
```



## Documentation

### Start Here
- **[Project Structure](./docs/PROJECT_STRUCTURE.md)** - How folders are organized
- **[Architecture Guide](./docs/ARCHITECTURE.md)** - How the system is organized
- **[Quick References](./docs/)** - One-page guides (QUICK_REFERENCE_*.md)

### By System
| System | Go to... |
|--------|----------|
| **Velinor Game** | `docs/VELINOR_*.md` |
| **FirstPerson AI** | `docs/FIRSTPERSON_*.md` |
| **Deployment** | `docs/DEPLOYMENT_*.md` |
| **Code structure** | `docs/ARCHITECTURE.md` |
##

## Project Structure (Post-Reorganization)

```
saoriverse-console/
├── app.py                 # Single Streamlit entry point
├── requirements.txt       # Dependencies
├── pytest.ini            # Test configuration
│
├── src/                  # Core application (25 modules)
├── tests/                # All tests (unit + integration)
├── data/                 # Data files (glyphs, lexicons)
├── scripts/              # Utility scripts (organized)
├── docs/                 # Documentation
```text
```



**Key Change**: Flat `src/` directory with no deep nesting, single `app.py` entry point.
##

## Running Tests

```bash

# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage report
```text
```


##

## Architecture

### Text-to-Response Pipeline

```
```text
```



### Voice Pipeline (Optional)

```
```text
```



### Learning System

```
```text
```


##

## Core Modules

| Module | Purpose |
|--------|---------|
| `src/response_generator.py` | Main orchestrator |
| `src/signal_parser.py` | Text → emotional signals |
| `src/enhanced_response_composer.py` | Compose responses |
| `src/voice_interface.py` | Voice I/O (optional) |
| `src/streaming_tts.py` | Text-to-speech |
| `src/audio_pipeline.py` | Speech-to-text |
| `src/relational_memory.py` | Memory/persistence |

See `docs/ARCHITECTURE.md` for complete module reference.
##

## Development

### Add a New Feature
1. Create code in `src/`
2. Add tests to `tests/unit/` or `tests/integration/`
3. Run `pytest tests/` to verify
4. Update documentation if needed

### Fix a Bug
1. Write a test that reproduces the bug
2. Fix the code
3. Verify test passes: `pytest tests/`
4. Commit with test
##

## Privacy & Local-First

- ✅ All processing runs locally
- ✅ No data leaves your computer
- ✅ No cloud dependencies
- ✅ Optional: Connect to remote AI (disabled by default)
##

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.
##

## Documentation Index

- **[Architecture Guide](./docs/ARCHITECTURE.md)** - System design and module reference
- **[Testing Guide](./docs/TESTING_GUIDE.md)** - How to test
- **[API Reference](./docs/API_REFERENCE.md)** - Public APIs for all modules
- **[Full Index](./docs/INDEX.md)** - All documentation
##

## Troubleshooting

### Port Already in Use

```bash

# Kill the process using port 8501
lsof -i :8501
kill -9 <PID>

# Then restart
```text
```



### Import Errors

```bash

# Ensure you're in the project root
cd saoriverse-console

# Verify Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
```text
```



### Tests Not Running

```bash

# Check pytest is installed
python -m pytest --version

# Run with verbose output
pytest tests/ -v
```


##

## Version History

**Post-Reorganization (Dec 3, 2025)**
- Phases 1-9 complete
- Flat src/ structure (25 modules)
- 26 unit tests + 11 integration tests
- Single app.py entry point
- Ready for production
##

**Questions?** See `docs/INDEX.md` for the complete documentation index.
