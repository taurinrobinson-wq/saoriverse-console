# SaoriVerse Console - FirstPerson

A private, local-first emotional AI companion with integrated voice interface.

**Status**: Post-reorganization (Phase 9) - Clean, modular architecture

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```

Opens automatically in your browser at `http://localhost:8501`

### 3. (Optional) Enable Voice
Configure voice settings in the sidebar when running app.py

---

## Documentation

### Start Here
- **[Architecture Guide](./docs/ARCHITECTURE.md)** - How the system is organized
- **[Testing Guide](./docs/TESTING_GUIDE.md)** - How to run and write tests
- **[API Reference](./docs/API_REFERENCE.md)** - All public APIs

### Quick Navigation
| Need... | Go to... |
|---------|----------|
| Code structure | `docs/ARCHITECTURE.md` |
| Run tests | `docs/TESTING_GUIDE.md` |
| API documentation | `docs/API_REFERENCE.md` |
| Full docs index | `docs/INDEX.md` |

---

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
└── archive/              # Old code/docs (for reference)
```

**Key Change**: Flat `src/` directory with no deep nesting, single `app.py` entry point.

---

## Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage report
pytest tests/ --cov=src
```

---

## Architecture

### Text-to-Response Pipeline
```
User Input → Signal Parser → Response Generator → Streamlit UI
```

### Voice Pipeline (Optional)
```
Audio Input → STT → [same as above] → TTS → Audio Output
```

### Learning System
```
User Feedback → Pattern Learning → Memory Storage → Improvement
```

---

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

---

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

---

## Privacy & Local-First

- ✅ All processing runs locally
- ✅ No data leaves your computer
- ✅ No cloud dependencies
- ✅ Optional: Connect to remote AI (disabled by default)

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## Documentation Index

- **[Architecture Guide](./docs/ARCHITECTURE.md)** - System design and module reference
- **[Testing Guide](./docs/TESTING_GUIDE.md)** - How to test
- **[API Reference](./docs/API_REFERENCE.md)** - Public APIs for all modules
- **[Full Index](./docs/INDEX.md)** - All documentation

---

## Troubleshooting

### Port Already in Use
```bash
# Kill the process using port 8501
lsof -i :8501
kill -9 <PID>

# Then restart
streamlit run app.py
```

### Import Errors
```bash
# Ensure you're in the project root
cd saoriverse-console

# Verify Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Not Running
```bash
# Check pytest is installed
python -m pytest --version

# Run with verbose output
pytest tests/ -v
```

---

## Version History

**Post-Reorganization (Dec 3, 2025)**
- Phases 1-9 complete
- Flat src/ structure (25 modules)
- 26 unit tests + 11 integration tests
- Single app.py entry point
- Ready for production

---

**Questions?** See `docs/INDEX.md` for the complete documentation index.
